<template>
  <Calendar
    v-model:events="calendarEvents"
    :columns="columnsToDisplay"
    @dragstart="setCurrentScheduledCourse"
    @update:week="changeDate"
    :end-of-day-hours="endOfDay"
  />
  <TooltipProvider>
    <TooltipRoot>
      <TooltipTrigger>
        <button @click="availabilityToggle = !availabilityToggle" style="background-color: black; color: white">
          Availabilities
        </button>
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent as-child class="TooltipContent" :side-offset="5">
          Showing your availabilities
          <TooltipArrow class="TooltipArrow" size="8" />
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>

<script setup lang="ts">
import { CalendarColumn } from '@/components/calendar/declaration'
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
  nextDay,
  today,
  updateFormatted,
} from '@quasar/quasar-ui-qcalendar'
import { filter } from 'lodash'
import { useRoomStore } from '@/stores/timetable/room'
import { Group } from '@/stores/declarations'
import { useTutorStore } from '@/stores/timetable/tutor'
import { useDepartmentStore } from '@/stores/department'
import { usePermanentStore } from '@/stores/timetable/permanent'
import { useAuth } from '@/stores/auth'
import { useAvailabilityStore } from '@/stores/timetable/availability'
import { useEventStore } from '@/stores/display/event'
import { TooltipArrow, TooltipContent, TooltipPortal, TooltipProvider, TooltipRoot, TooltipTrigger } from 'radix-vue'
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
const availabilityStore = useAvailabilityStore()
const permanentStore = usePermanentStore()
const { columns } = storeToRefs(columnStore)
const { daysSelected, calendarEvents } = storeToRefs(eventStore)
const tutorStore = useTutorStore()
const deptStore = useDepartmentStore()
const selectedGroups = ref<Group[]>([])
const sunday = ref<Timestamp>()
const monday = ref<Timestamp>()
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
}

function changeDate(newDate: Timestamp) {
  monday.value = updateFormatted(getStartOfWeek(newDate, [1, 2, 3, 4, 5, 6, 0]))
  sunday.value = updateFormatted(getEndOfWeek(monday.value, [1, 2, 3, 4, 5, 6, 0]))
  fetchScheduledCurrentWeek(makeDate(monday.value), makeDate(sunday.value))
  fetchAvailCurrentWeek(makeDate(monday.value), makeDate(sunday.value))
  let currentDate = copyTimestamp(monday.value!)
  daysSelected.value = []
  while (currentDate.weekday !== sunday.value!.weekday) {
    daysSelected.value.push(copyTimestamp(currentDate))
    currentDate = updateFormatted(nextDay(currentDate))
  }
}

/**
 * Fetching data required on mount
 */
onBeforeMount(async () => {
  let todayDate: Timestamp = updateFormatted(parsed(today()))
  monday.value = updateFormatted(getStartOfWeek(todayDate, [1, 2, 3, 4, 5, 6, 0]))
  sunday.value = updateFormatted(getEndOfWeek(monday.value, [1, 2, 3, 4, 5, 6, 0]))
  let currentDate = copyTimestamp(monday.value!)
  daysSelected.value = []
  while (currentDate.weekday !== sunday.value!.weekday) {
    daysSelected.value.push(copyTimestamp(currentDate))
    currentDate = updateFormatted(nextDay(currentDate))
  }
  fetchScheduledCurrentWeek(makeDate(monday.value), makeDate(sunday.value))
  fetchAvailCurrentWeek(makeDate(monday.value), makeDate(sunday.value))
  roomStore.fetchRooms()
  tutorStore.fetchTutors()
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
