<template>
  <q-btn
    round
    color="primary"
    :icon="matBatteryFull"
    style="margin: 5px"
    @click="availabilityToggle = !availabilityToggle"
  />
  <FilterSelector
    :items="roomsFetched"
    filter-selector-undefined-label="Select a room"
    v-model:selected-items="selectedRoom"
    :multiple="false"
    item-variable-name="name"
  />
  <Calendar
    v-model:events="calendarEvents"
    :columns="columnsToDisplay"
    @dragstart="setCurrentScheduledCourse"
    @update:week="changeDate"
    :end-of-day-minutes="19"
  />
</template>

<script setup lang="ts">
import { CalendarColumn, InputCalendarEvent } from '@/components/calendar/declaration'
import Calendar from '@/components/calendar/Calendar.vue'
import { computed, onBeforeMount, ref, watchEffect } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { useGroupStore } from '@/stores/timetable/group'
import { useColumnStore } from '@/stores/display/column'
import { storeToRefs } from 'pinia'
import { parsed } from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'
import {
  Timestamp,
  copyTimestamp,
  makeDate,
  nextDay,
  parseTime,
  prevDay,
  relativeDays,
  today,
  updateFormatted,
} from '@quasar/quasar-ui-qcalendar'
import { filter } from 'lodash'
import FilterSelector from '@/components/utils/FilterSelector.vue'
import { useRoomStore } from '@/stores/timetable/room'
import { Room } from '@/stores/declarations'
import { useTutorStore } from '@/stores/timetable/tutor'
import { useDepartmentStore } from '@/stores/department'
import { matBatteryFull } from '@quasar/extras/material-icons'

/**
 * Data translated to be passed to components
 */
const calendarEvents = ref<InputCalendarEvent[]>([])
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
const { courses } = storeToRefs(scheduledCourseStore)
const { columns } = storeToRefs(columnStore)
const { roomsFetched } = storeToRefs(roomStore)
const tutorStore = useTutorStore()
const deptStore = useDepartmentStore()
const selectedRoom = ref<Room>()

watchEffect(() => {
  calendarEvents.value = courses.value
    .map((c) => {
      const currentEvent: InputCalendarEvent = {
        id: id++,
        title: c.module ? c.module.toString() : 'Cours',
        toggled: !selectedRoom.value || c.room === selectedRoom.value.id,
        bgcolor: id % 2 === 0 ? 'red' : 'blue',
        columnIds: [],
        data: {
          dataId: c.id,
          dataType: 'event',
          start: copyTimestamp(c.start),
          duration: parseTime(c.end) - parseTime(c.start),
        },
      }
      c.groupIds.forEach((courseGroup) => {
        const currentGroup = groupStore.groups.find((g) => g.id === courseGroup)
        if (currentGroup) {
          currentGroup.columnIds.forEach((cI) => {
            currentEvent.columnIds.push(cI)
          })
        }
      })
      return currentEvent
    })
    .filter((ce) => ce.columnIds.length > 0)
})

const currentScheduledCourseId = ref<number | null>(null)
function setCurrentScheduledCourse(scheduledCourseId: number) {
  currentScheduledCourseId.value = scheduledCourseId
}

function fetchScheduledCurrentWeek(from: Date, to: Date) {
  scheduledCourseStore.fetchScheduledCourses((from = from), (to = to), deptStore.current.id)
}

function changeDate(newDate: Timestamp) {
  const newMonday = updateFormatted(relativeDays(copyTimestamp(newDate), prevDay, newDate.weekday - 1 || 6))
  const newSunday = updateFormatted(relativeDays(copyTimestamp(newMonday), nextDay, 6))
  fetchScheduledCurrentWeek(makeDate(newMonday), makeDate(newSunday))
}

/**
 * Fetching data required on mount
 */
onBeforeMount(async () => {
  let todayDate = updateFormatted(parsed(today()))
  fetchScheduledCurrentWeek(
    makeDate(todayDate),
    makeDate(updateFormatted(relativeDays(todayDate, nextDay, todayDate.weekday - 1 || 6)))
  )
  roomStore.fetchRooms()
  tutorStore.fetchTutors(deptStore.current)
  if (!deptStore.isCurrentDepartmentSelected) deptStore.getDepartmentFromURL()
  groupStore.fetchGroups(deptStore.current)
})
</script>

<style scoped>
.ac {
  background-color: rgba(25, 124, 25, 0.685);
}
.nac {
  background-color: rgb(133, 34, 34);
}
</style>
