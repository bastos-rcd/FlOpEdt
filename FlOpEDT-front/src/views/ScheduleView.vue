<template>
  <q-btn
    round
    color="primary"
    :icon="matBatteryFull"
    style="margin: 5px"
    @click="availabilityToggle = !availabilityToggle"
  />
  <Calendar
    v-model:events="calendarEvents"
    :columns="columnsToDisplay"
    @dragstart="setCurrentScheduledCourse"
    @update:week="changeDate"
    :end-of-day-minutes="19"
  />
  <HierarchicalColumnFilter v-model:active-ids="activeIds" :flatNodes="(flatNodes as LinkIdUp[])">
    <template #item="{ nodeId, active }">
      <div :class="['node', active ? 'ac' : 'nac']">
        {{ find(flatNodes, (n) => n.id === nodeId)?.name }}
        {{ active }}
      </div>
    </template>
  </HierarchicalColumnFilter>
  <FilterSelector
    :items="roomsFetched"
    filter-selector-undefined-label="Select a room"
    v-model:selected-items="selectedRoom"
    :multiple="false"
    item-variable-name="name"
  />
<!-- <button @click="revertUpdate">Revert</button> -->
</template>

<script setup lang="ts">
import { CalendarColumn, InputCalendarEvent } from '@/components/calendar/declaration'
import HierarchicalColumnFilter from '@/components/hierarchicalFilter/HierarchicalColumnFilter.vue'
import Calendar from '@/components/calendar/Calendar.vue'
import { computed, onBeforeMount, ref, watchEffect } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { useGroupStore } from '@/stores/timetable/group'
import { useColumnStore } from '@/stores/display/column'
import { storeToRefs } from 'pinia'
import { parsed } from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'
import { Timestamp, copyTimestamp, getDate, makeDate, nextDay, parseTime, relativeDays, today, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'
import { filter, find } from 'lodash'
import FilterSelector from '@/components/utils/FilterSelector.vue'
import { useRoomStore } from '@/stores/timetable/room'
import { Room } from '@/stores/declarations'
import { useTutorStore } from '@/stores/timetable/tutor'
import { useDepartmentStore } from '@/stores/department'
import { LinkIdUp } from '@/ts/tree'
import { matBatteryFull } from '@quasar/extras/material-icons'

/**
 * Data translated to be passed to components
 */
const calendarEvents = ref<InputCalendarEvent[]>([])
const activeIds = ref<Array<number>>([])
const availabilityToggle = ref<boolean>(false)
const flatNodes = computed(() => {
  return groups.value
})
let id = 1

const columnsToDisplay = computed(() => {
  return filter(columns.value, (c: CalendarColumn) => {
    return find(activeIds.value, (ai) => {
      if (availabilityToggle.value) return ai === c.id || c.name === 'Avail'
      return ai === c.id
    })
  }) as CalendarColumn[]
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
const { groups } = storeToRefs(groupStore)
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
        title: c.module.toString(),
        toggled: !selectedRoom.value || c.room === selectedRoom.value.id,
        bgcolor: 'red',
        columnIds: [],
        data: {
          dataId: c.id,
          dataType: 'event',
          start: copyTimestamp(c.start),
          duration: parseTime(c.end) - parseTime(c.start),
        },
      }
      currentEvent.data.start.date = getDate(currentEvent.data.start)
      c.groupIds.forEach((courseGroup) => {
        const currentGroup = groups.value.find((g) => g.id === courseGroup)
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
  scheduledCourseStore.fetchScheduledCourses(from = from, to = to)
}

function changeDate(newDate: Timestamp) {
  fetchScheduledCurrentWeek(makeDate(newDate), makeDate(relativeDays(newDate, nextDay, 6)))
}

/**
 * Fetching data required on mount
 */
onBeforeMount(async () => {
  let todayDate = updateWorkWeek(parsed(today()) as Timestamp)
  fetchScheduledCurrentWeek(makeDate(todayDate), makeDate(relativeDays(todayDate)))
  roomStore.fetchRooms()
  tutorStore.fetchTutors(deptStore.current)
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
