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
    :end-of-day-minutes="19"
  />
</template>

<script setup lang="ts">
import { CalendarColumn, InputCalendarEvent } from '@/components/calendar/declaration'
import Calendar from '@/components/calendar/Calendar.vue'
import { computed, onBeforeMount, ref, watch, watchEffect } from 'vue'
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
import { Group, Module, Room } from '@/stores/declarations'
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
const authStore = useAuth()
const availabilityStore = useAvailabilityStore()
const permanentStore = usePermanentStore()
const { availabilities } = storeToRefs(availabilityStore)
const { courses } = storeToRefs(scheduledCourseStore)
const { fetchedTransversalGroups } = storeToRefs(groupStore)
const { columns } = storeToRefs(columnStore)
const { roomsFetched } = storeToRefs(roomStore)
const { modules } = storeToRefs(permanentStore)
const tutorStore = useTutorStore()
const deptStore = useDepartmentStore()
const selectedRoom = ref<Room>()
const selectedGroups = ref<Group[]>([])
const moduleColor: Map<number, string> = new Map<number, string>()

watch(selectedGroups, () => {
  groupStore.clearSelected()
  if (selectedGroups.value !== null) selectedGroups.value.forEach((gp) => groupStore.addTransversalGroupToSelection(gp))
})

watchEffect(() => {
  if (modules.value.length > 0) {
    attributeColorToModule()
  }
})

watchEffect(() => {
  calendarEvents.value = _.union(
    courses.value
      .map((c) => {
        const module: Module | undefined = modules.value.find((m) => m.id === c.module)
        let color: string | undefined
        if (module) color = moduleColor.get(module.id)
        const currentEvent: InputCalendarEvent = {
          id: id++,
          title: module ? module.abbrev : 'Cours',
          toggled: !selectedRoom.value || c.room === selectedRoom.value.id,
          bgcolor: color ? color : 'blue',
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
      .filter((ce) => ce.columnIds.length > 0),
    availabilities.value.map((av) => {
      const currentEvent: InputCalendarEvent = {
        id: id++,
        title: '1',
        toggled: true,
        bgcolor: '',
        columnIds: [],
        data: {
          dataId: av.id,
          dataType: 'avail',
          start: copyTimestamp(av.start),
          duration: av.duration,
        },
      }
      const availColumn = columns.value.find((c) => c.name === 'Avail')
      if (availColumn) currentEvent.columnIds.push(availColumn.id)
      return currentEvent
    })
  )
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
  const newMonday: Timestamp = updateFormatted(getStartOfWeek(newDate, [1, 2, 3, 4, 5, 6, 0]))
  const newSunday: Timestamp = updateFormatted(getEndOfWeek(newMonday, [1, 2, 3, 4, 5, 6, 0]))
  fetchScheduledCurrentWeek(makeDate(newMonday), makeDate(newSunday))
  fetchAvailCurrentWeek(makeDate(newMonday), makeDate(newSunday))
}

/**
 * Fetching data required on mount
 */
onBeforeMount(async () => {
  let todayDate: Timestamp = updateFormatted(parsed(today()))
  fetchScheduledCurrentWeek(makeDate(todayDate), makeDate(getEndOfWeek(todayDate, [1, 2, 3, 4, 5, 6, 0])))
  fetchAvailCurrentWeek(makeDate(todayDate), makeDate(getEndOfWeek(todayDate, [1, 2, 3, 4, 5, 6, 0])))
  roomStore.fetchRooms()
  tutorStore.fetchTutors(deptStore.current)
  if (!deptStore.isCurrentDepartmentSelected) deptStore.getDepartmentFromURL()
  groupStore.fetchGroups(deptStore.current)
  permanentStore.fetchModules()
})

function attributeColorToModule(): void {
  moduleColor.clear() // Clear the map to avoid duplicates
  modules.value.forEach((mod: Module) => {
    const colorValue =
      'rgb(' +
      Math.ceil(Math.random() * 255) +
      ',' +
      Math.ceil(Math.random() * 255) +
      ',' +
      Math.ceil(Math.random() * 255) +
      ')'
    moduleColor.set(mod.id, colorValue)
  })
}
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
