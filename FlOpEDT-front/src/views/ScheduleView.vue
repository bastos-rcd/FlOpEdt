<template>
  <div class="header">
    <FilterSelector
      :items="roomsFetched"
      filter-selector-undefined-label="Room Selection"
      v-model:selected-items="selectedRoom"
      :multiple="false"
      item-variable-name="name"
      style="flex-grow: 2; max-width: 20%"
    />
    <FilterSelector
      :items="fetchedTransversalGroups"
      filter-selector-undefined-label="Group Selection"
      v-model:selected-items="selectedGroups"
      :multiple="true"
      item-variable-name="name"
      style="flex-grow: 2; max-width: 20%"
    />
    <q-btn
      v-if="authStore.isUserAuthenticated"
      round
      color="primary"
      :icon="matBatteryFull"
      style="margin: 5px"
      @click="availabilityToggle = !availabilityToggle"
    />
  </div>
  <Calendar
    v-model:events="calendarEvents"
    :columns="columnsToDisplay"
    @dragstart="setCurrentScheduledCourse"
    @update:week="changeDate"
    :end-of-day-minutes="endOfDay"
  />
</template>

<script setup lang="ts">
import { CalendarColumn, InputCalendarEvent } from '@/components/calendar/declaration'
import Calendar from '@/components/calendar/Calendar.vue'
import { computed, onBeforeMount, ref, watch } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { useGroupStore } from '@/stores/timetable/group'
import { useColumnStore } from '@/stores/display/column'
import { storeToRefs } from 'pinia'
import { parsed } from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'
import {
  Timestamp,
  copyTimestamp,
  getEndOfWeek,
  getStartOfWeek,
  makeDate,
  parseTime,
  today,
  updateFormatted,
} from '@quasar/quasar-ui-qcalendar'
import { filter } from 'lodash'
import FilterSelector from '@/components/utils/FilterSelector.vue'
import { useRoomStore } from '@/stores/timetable/room'
import { Group, Room } from '@/stores/declarations'
import { useTutorStore } from '@/stores/timetable/tutor'
import { useDepartmentStore } from '@/stores/department'
import { matBatteryFull } from '@quasar/extras/material-icons'
import { usePermanentStore } from '@/stores/timetable/permanent'
import { useAuth } from '@/stores/auth'
import { useAvailabilityStore } from '@/stores/timetable/availability'
import _ from 'lodash'

/**
 * Data translated to be passed to components
 */
const calendarEvents = computed({
  get() {
    const calendarEventsToReturn: InputCalendarEvent[] = scheduledCourseStore.getCalendarCoursesFromDateToDate(
      monday.value!,
      sunday.value!
    )
    calendarEventsToReturn.forEach((c) => {
      if (c.id === -1) c.id = id++
      calendarEventsPrev.set(c.id, c)
    })
    availabilities.value.forEach((av) => {
      const currentEvent: InputCalendarEvent = {
        id: av.id === -1 ? id++ : av.id,
        title: '',
        toggled: true,
        bgcolor: '',
        columnIds: [],
        data: {
          dataId: av.id,
          dataType: 'avail',
          start: copyTimestamp(av.start),
          duration: av.duration,
          value: av.value,
        },
      }
      currentEvent.title = currentEvent.id.toString()
      const availColumn = columns.value.find((c) => c.name === 'Avail')
      if (availColumn) currentEvent.columnIds.push(availColumn.id)
      calendarEventsToReturn!.push(currentEvent)
      calendarEventsPrev.set(currentEvent.id, currentEvent)
    })
    return calendarEventsToReturn
  },
  set(value: InputCalendarEvent[]) {
    value.forEach((v) => {
      const previousEvent = calendarEventsPrev.get(v.id)
      if (
        !previousEvent ||
        !_.isEqual(v, previousEvent) ||
        parseTime(v.data.start.time) + v.data.duration! >= endOfDay * 60
      ) {
        if (v.data.dataType === 'event') scheduledCourseStore.addCalendarCourseToDate(v)
        else if (v.data.dataType === 'avail') availabilityStore.addOrUpdateAvailibility(v, authStore.getUser.id)
      }
      calendarEventsPrev.delete(v.id)
    })
    calendarEventsPrev.forEach((event, id) => {
      availabilityStore.removeAvailibility(id)
    })
    value.forEach((v) => {
      calendarEventsPrev.set(v.id, v)
    })
  },
})
const availabilityToggle = ref<boolean>(false)
let id = 1

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
const columnStore = useColumnStore()
const scheduledCourseStore = useScheduledCourseStore()
const roomStore = useRoomStore()
const authStore = useAuth()
const availabilityStore = useAvailabilityStore()
const permanentStore = usePermanentStore()
const { availabilities } = storeToRefs(availabilityStore)
const { fetchedTransversalGroups } = storeToRefs(groupStore)
const { columns } = storeToRefs(columnStore)
const { roomsFetched } = storeToRefs(roomStore)
const tutorStore = useTutorStore()
const deptStore = useDepartmentStore()
const selectedRoom = ref<Room>()
const selectedGroups = ref<Group[]>([])
const sunday = ref<Timestamp>()
const monday = ref<Timestamp>()
const calendarEventsPrev: Map<number, InputCalendarEvent> = new Map<number, InputCalendarEvent>()
const endOfDay = 19

watch(selectedGroups, () => {
  groupStore.clearSelected()
  if (selectedGroups.value !== null) selectedGroups.value.forEach((gp) => groupStore.addTransversalGroupToSelection(gp))
})

const currentScheduledCourseId = ref<number | null>(null)
function setCurrentScheduledCourse(scheduledCourseId: number) {
  currentScheduledCourseId.value = scheduledCourseId
}

function fetchScheduledCurrentWeek(from: Date, to: Date) {
  scheduledCourseStore.fetchScheduledCourses((from = from), (to = to), -1, deptStore.current)
}

function fetchAvailCurrentWeek(from: Date, to: Date) {
  availabilityStore.fetchUserAvailabilitiesBack(authStore.getUser.id, from, to)
  console.log('id: ', authStore.getUser.id)
}

function changeDate(newDate: Timestamp) {
  monday.value = updateFormatted(getStartOfWeek(newDate, [1, 2, 3, 4, 5, 6, 0]))
  sunday.value = updateFormatted(getEndOfWeek(monday.value, [1, 2, 3, 4, 5, 6, 0]))
  fetchScheduledCurrentWeek(makeDate(monday.value), makeDate(sunday.value))
  fetchAvailCurrentWeek(makeDate(monday.value), makeDate(sunday.value))
}

/**
 * Fetching data required on mount
 */
onBeforeMount(async () => {
  let todayDate: Timestamp = updateFormatted(parsed(today()))
  monday.value = updateFormatted(getStartOfWeek(todayDate, [1, 2, 3, 4, 5, 6, 0]))
  sunday.value = updateFormatted(getEndOfWeek(monday.value, [1, 2, 3, 4, 5, 6, 0]))
  fetchScheduledCurrentWeek(makeDate(monday.value), makeDate(sunday.value))
  fetchAvailCurrentWeek(makeDate(monday.value), makeDate(sunday.value))
  roomStore.fetchRooms()
  tutorStore.fetchTutors(deptStore.current)
  if (!deptStore.isCurrentDepartmentSelected) deptStore.getDepartmentFromURL()
  groupStore.fetchGroups(deptStore.current)
  permanentStore.fetchModules()
})
</script>

<style scoped>
.ac {
  background-color: rgba(25, 124, 25, 0.685);
}
.nac {
  background-color: rgb(133, 34, 34);
}
.header {
  display: flex;
  justify-content: space-between;
}
</style>
