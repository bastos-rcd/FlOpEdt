<template>
  <div class="content">
    <div v-if="authStore.sidePanelToggle" class="side-panel" :class="{ open: authStore.sidePanelToggle }">
      <SidePanel
        v-if="authStore.sidePanelToggle"
        v-model:workcopy="workcopySelected"
        v-model:weekdays="daysToDisplay"
        v-model:availChecked="availabilityToggle"
        v-model:isInEdit="isInEditMode"
        v-model:tutor-as="tutorSelectedForAvail"
        v-model:calendar-type="calendarTypeModel"
        :rooms="roomsFetched"
        :tutors="tutors"
        :groups="fetchedStructuralGroups.filter((g) => g.columnIds.length === 1)"
        :revert="undoRedo.hasUpdate.value && isInEditMode"
        @revert-update="() => undoRedo.revertUpdateBlock()"
      />
    </div>
    <div class="main-content" :class="{ open: authStore.sidePanelToggle }">
      <Calendar
        v-model:events="calendarEvents"
        v-model:calendar-type="calendarTypeModel"
        :columns="columnsToDisplay"
        :dropzones="dropzonesToDisplay"
        :start-of-day="timeSettings.get(current.id)!.dayStartTime"
        :end-of-day="timeSettings.get(current.id)!.dayEndTime"
        :workcopy="workcopySelected"
        :interval-minutes="intervalMinutes"
        :is-in-edit="isInEditMode"
        :weekdays-string="daysToDisplay"
        @update:events="handleUpdateEvents"
        @dragstart="onDragStart"
        @update:week="changeDate"
        @delete:event="handleDeleteEvent"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { CalendarColumn, CalendarEvent, InputCalendarEvent } from '@/components/calendar/declaration'
import Calendar from '@/components/calendar/Calendar.vue'
import { computed, onBeforeMount, ref, watch } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { useGroupStore } from '@/stores/timetable/group'
import { useColumnStore } from '@/stores/display/column'
import { storeToRefs } from 'pinia'
import {
  Timestamp,
  copyTimestamp,
  getEndOfWeek,
  getStartOfWeek,
  makeDate,
  nextDay,
  parseTime,
  today,
  updateFormatted,
  updateMinutes,
  parsed,
  getStartOfMonth,
  getEndOfMonth,
} from '@quasar/quasar-ui-qcalendar'
import { filter } from 'lodash'
import { useRoomStore } from '@/stores/timetable/room'
import { Group, User } from '@/stores/declarations'
import { useTutorStore } from '@/stores/timetable/tutor'
import { useDepartmentStore } from '@/stores/department'
import { useAuth } from '@/stores/auth'
import { useAvailabilityStore } from '@/stores/timetable/availability'
import { useEventStore } from '@/stores/display/event'
import SidePanel from '@/components/SidePanel.vue'
import { createDropzonesForEvent } from '@/components/calendar/utilitary'
import { usePermanentStore } from '@/stores/timetable/permanent'
import { useUndoredo } from '@/composables/undoredo'
import { AvailabilityData, CourseData } from '@/composables/declaration'
/**
 * Data translated to be passed to components
 */
const availabilityToggle = ref<boolean>(false)

const columnsToDisplay = computed(() => {
  if (availabilityToggle.value) return columns.value
  return filter(columns.value, (c: CalendarColumn) => c.name !== 'Avail')
})

/**
 * API data waiting to be translated in Calendar events
 * * The scheduledCourses becoming events
 * * The groups and columns helping to put events in schedule
 */
const groupStore = useGroupStore()
const eventStore = useEventStore()
const columnStore = useColumnStore()
const scheduledCourseStore = useScheduledCourseStore()
const roomStore = useRoomStore()
const authStore = useAuth()
const tutorStore = useTutorStore()
const deptStore = useDepartmentStore()
const permanentStore = usePermanentStore()
const undoRedo = useUndoredo()
const availabilityStore = useAvailabilityStore()
const { current } = storeToRefs(deptStore)
const { columns } = storeToRefs(columnStore)
const { daysSelected, calendarEvents, dropzonesIds } = storeToRefs(eventStore)
const { roomsFetched } = storeToRefs(roomStore)
const { tutors } = storeToRefs(tutorStore)
const { fetchedStructuralGroups } = storeToRefs(groupStore)
const { timeSettings, intervalMinutes, calendarType } = storeToRefs(permanentStore)
const selectedGroups = ref<Group[]>([])
const dropzonesToDisplay = ref<CalendarEvent[]>([])
const isInEditMode = ref<boolean>(false)
const daysToDisplay = ref<string[]>(['mo', 'tu', 'we', 'th', 'fr'])
const last = ref<Timestamp>()
const first = ref<Timestamp>()
const workcopySelected = ref<number>(-1)
const tutorSelectedForAvail = ref<User>()
const calendarTypeModel = computed({
  get() {
    return calendarType.value
  },
  set(v: string) {
    calendarType.value = v
  },
})

watch(selectedGroups, () => {
  groupStore.clearSelected()
  if (selectedGroups.value !== null) selectedGroups.value.forEach((gp) => groupStore.addTransversalGroupToSelection(gp))
})

watch(tutorSelectedForAvail, () => {
  if (tutorSelectedForAvail.value)
    fetchCurrentAvail(makeDate(first.value!), makeDate(last.value!), tutorSelectedForAvail.value.id)
  else fetchCurrentAvail(makeDate(first.value!), makeDate(last.value!))
})

function onDragStart(eventId: number, allEvents: CalendarEvent[]) {
  const timeSetting = timeSettings.value.get(current.value.id)
  let dayStartTime: number
  let dayEndTime: number
  let lunchBreakStart: number
  let lunchBreakEnd: number
  if (timeSetting) {
    dayStartTime = timeSetting.dayStartTime
    dayEndTime = timeSetting.dayEndTime
    lunchBreakStart = timeSetting.morningEndTime
    lunchBreakEnd = timeSetting.afternoonStartTime
    if (dayStartTime && dayEndTime) {
      const dropzones: CalendarEvent[] = createDropzonesForEvent(
        eventId,
        allEvents,
        dayStartTime,
        dayEndTime,
        6,
        lunchBreakStart,
        lunchBreakEnd
      )
      dropzones.forEach((dz) => {
        dz.id = dropzonesIds.value
        dropzonesIds.value += 2
      })
      dropzonesToDisplay.value = dropzones
    }
  }
}

function fetchCurrentScheduled(from: Date, to: Date) {
  void scheduledCourseStore.fetchScheduledCourses(from, to, -1, deptStore.current)
}

function fetchCurrentAvail(from: Date, to: Date, tutorId?: number) {
  void availabilityStore.fetchUserAvailabilitiesBack(tutorId ? tutorId : authStore.getUser.id, from, to)
}

function changeDate(newDate: Timestamp) {
  if (calendarTypeModel.value === 'week' || calendarTypeModel.value === 'day') {
    first.value = updateFormatted(getStartOfWeek(newDate, [1, 2, 3, 4, 5, 6, 0]))
    last.value = updateFormatted(getEndOfWeek(first.value, [1, 2, 3, 4, 5, 6, 0]))
  } else if (calendarTypeModel.value === 'month') {
    first.value = updateFormatted(getStartOfMonth(newDate))
    last.value = updateFormatted(getEndOfMonth(newDate))
  }
  fetchCurrentScheduled(makeDate(first.value!), makeDate(last.value!))
  fetchCurrentAvail(makeDate(first.value!), makeDate(last.value!))
  let currentDate = copyTimestamp(first.value!)
  daysSelected.value = []
  while (currentDate.date !== last.value!.date) {
    daysSelected.value.push(copyTimestamp(currentDate))
    currentDate = updateFormatted(nextDay(currentDate))
  }
}

watch(calendarTypeModel, () => {
  if (calendarTypeModel.value === 'week' || calendarTypeModel.value === 'day') {
    fetchCurrentScheduled(makeDate(first.value!), makeDate(last.value!))
    fetchCurrentAvail(makeDate(first.value!), makeDate(last.value!))
  } else if (calendarTypeModel.value === 'month') {
    first.value = updateFormatted(getStartOfMonth(first.value!))
    last.value = updateFormatted(getEndOfMonth(last.value!))
    fetchCurrentScheduled(makeDate(first.value), makeDate(last.value))
    fetchCurrentAvail(makeDate(first.value), makeDate(last.value))
    updateDaysSelected()
  }
})

function updateDaysSelected() {
  let currentDate = copyTimestamp(first.value!)
  daysSelected.value = []
  while (currentDate.date !== last.value!.date) {
    daysSelected.value.push(copyTimestamp(currentDate))
    currentDate = updateFormatted(nextDay(currentDate))
  }
}

function handleDeleteEvent(id: number): void {
  const course = scheduledCourseStore.getCourse(id)
  if (course)
    undoRedo.addUpdateBlock([
      {
        data: {
          tutorId: course.tutorId,
          start: course.start,
          end: course.end,
          roomId: course.room,
          suppTutorIds: course.suppTutorIds,
          graded: course.graded,
          roomTypeId: course.roomTypeId,
          groupIds: course.groupIds,
          moduleId: course.module,
          courseTypeId: course.courseTypeId,
        } as CourseData,
        objectId: id,
        type: 'course',
        operation: 'remove',
      },
    ])
}

function handleUpdateEvents(newCalendarEvents: InputCalendarEvent[]): void {
  let updatesData: {
    data: CourseData | AvailabilityData
    objectId: number
    type: 'course' | 'availability'
    operation: 'create' | 'update' | 'remove'
  }[] = []
  newCalendarEvents.forEach((newCalendarEvent) => {
    if (newCalendarEvent.data.dataType === 'event') {
      const course = scheduledCourseStore.getCourse(newCalendarEvent.data.dataId)
      if (course) {
        const courseData: CourseData = {
          tutorId: course.tutorId,
          start: newCalendarEvent.data.start,
          end: updateMinutes(
            copyTimestamp(newCalendarEvent.data.start),
            parseTime(newCalendarEvent.data.start) + newCalendarEvent.data.duration!
          ),
          roomId: course.room,
          suppTutorIds: course.suppTutorIds,
          graded: course.graded,
          roomTypeId: course.roomTypeId,
          groupIds: course.groupIds,
        }
        updatesData.push({
          data: courseData,
          objectId: newCalendarEvent.data.dataId,
          type: 'course',
          operation: 'update',
        })
      }
    } else if (newCalendarEvent.data.dataType === 'avail') {
      const availData: AvailabilityData = {
        start: newCalendarEvent.data.start,
        value: newCalendarEvent.data.value!,
        duration: newCalendarEvent.data.duration!,
      }
      const availability = availabilityStore.getAvailability(newCalendarEvent.data.dataId)
      let update = {
        data: availData,
        objectId: availability?.id || -1,
        type: 'availability' as 'course' | 'availability',
        operation: 'update' as 'create' | 'update' | 'remove',
        dataId: -1,
        availType: 'user',
      }
      if (newCalendarEvent.id === -1) {
        update.operation = 'create'
      } else if (!newCalendarEvent.data.duration || newCalendarEvent.data.duration <= 0) {
        update.operation = 'remove'
        update.dataId = availability!.dataId
        update.availType = availability!.type
      }
      if (availability) updatesData.push(update)
    }
  })
  undoRedo.addUpdateBlock(updatesData)
}

/**
 * Fetching data required on mount
 */
onBeforeMount(() => {
  let todayDate: Timestamp = updateFormatted(parsed(today()) as Timestamp)
  if (calendarTypeModel.value === 'week' || calendarTypeModel.value === 'day') {
    first.value = updateFormatted(getStartOfWeek(todayDate, [1, 2, 3, 4, 5, 6, 0]))
    last.value = updateFormatted(getEndOfWeek(first.value, [1, 2, 3, 4, 5, 6, 0]))
  } else if (calendarTypeModel.value === 'month') {
    first.value = updateFormatted(getStartOfMonth(todayDate))
    last.value = updateFormatted(getEndOfMonth(todayDate))
  }
  let currentDate = copyTimestamp(first.value!)
  daysSelected.value = []
  while (currentDate.date !== last.value!.date) {
    daysSelected.value.push(copyTimestamp(currentDate))
    currentDate = updateFormatted(nextDay(currentDate))
  }
  if (!deptStore.isCurrentDepartmentSelected) deptStore.getDepartmentFromURL()
  void groupStore.fetchGroups(deptStore.current)
  fetchCurrentScheduled(makeDate(first.value!), makeDate(last.value!))
  fetchCurrentAvail(makeDate(first.value!), makeDate(last.value!))
})
</script>

<style scoped>
.ac {
  background-color: rgba(25, 124, 25, 0.685);
}
.nac {
  background-color: rgb(133, 34, 34);
}
.side-panel {
  left: -300px; /* Initially hidden outside the viewport */
  position: relative;
  margin-right: 0.2%;
}
.main-content {
  width: 100%;
  flex: 1;
  position: relative;
}
.main-content.open {
  width: 84.8%;
  left: 0;
}
.side-panel.open {
  left: 0;
}
.content {
  display: flex;
}
</style>
