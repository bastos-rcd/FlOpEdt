<template>
  <Calendar
    v-model:events="calendarEvents"
    :columns="columnsToDisplay"
    @dragstart="setCurrentScheduledCourse"
    @update:week="changeDate"
  />
  <HierarchicalColumnFilter v-model:active-ids="activeIds" :flatNodes="flatNodes">
    <template #item="{ nodeId, active }">
      <div :class="['node', active ? 'ac' : 'nac']">
        {{ find(flatNodes, (n) => n.id === nodeId)?.name }}
        {{ active }}
      </div>
    </template>
  </HierarchicalColumnFilter>
  <button @click="revertUpdate">Revert</button>
</template>

<script setup lang="ts">
import { CalendarColumn, CalendarEvent } from '@/components/calendar/declaration'
import HierarchicalColumnFilter from '@/components/hierarchicalFilter/HierarchicalColumnFilter.vue'
import Calendar from '@/components/calendar/Calendar.vue'
import { computed, onBeforeMount, ref, watch } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { useGroupStore } from '@/stores/timetable/group'
import { useColumnStore } from '@/stores/display/column'
import { useUndoredo } from '@/composables/undoredo'
import { storeToRefs } from 'pinia'
import { parsed } from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'
import { Timestamp, today, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'
import { filter, find } from 'lodash'

/**
 * Data translated to be passed to components
 */
const calendarEvents = ref<CalendarEvent[]>([])
const activeIds = ref<Array<number>>([])
const flatNodes = computed(() => {
  return groups.value
})
let id = 1

const columnsToDisplay = computed(() => {
  return filter(columns.value, (c: CalendarColumn) => {
    return find(activeIds.value, (ai) => ai === c.id)
  }) as CalendarColumn[]
})

const { revertUpdate } = useUndoredo()

/**
 * API data waiting to be translated in Calendar events
 * * The scheduledCourses becoming events
 * * The groups and columns helping to put events in schedule
 */
const groupStore = useGroupStore()
const columnStore = useColumnStore()
const scheduledCourseStore = useScheduledCourseStore()
const { scheduledCourses } = storeToRefs(scheduledCourseStore)
const { groups } = storeToRefs(groupStore)
const { columns } = storeToRefs(columnStore)

watch(
  () => scheduledCourses.value,
  () => {
    calendarEvents.value = scheduledCourses.value
      .map((s) => {
        let timeS = updateWorkWeek(
          parsed(s.start_time.toString().substring(0, 10) + ' ' + s.start_time.toString().substring(11))
        )
        timeS.date = timeS.date.substring(0, 10)
        const currentEvent: CalendarEvent = {
          id: id++,
          title: s.course.type.name,
          toggled: true,
          bgcolor: s.course.module.display.color_bg,
          displayData: [],
          data: {
            dataId: s.id,
            dataType: 'event',
            start: timeS,
            duration: s.course.type.duration,
          },
        }
        s.course.groups.forEach((courseGroup) => {
          const currentGroup = groups.value.find((g) => g.id === courseGroup.id)
          if (currentGroup) {
            currentGroup.columnIds.forEach((cI) => {
              currentEvent.displayData.push({ columnId: cI, weight: 1 })
            })
          }
        })
        return currentEvent
      })
      .filter((ce) => ce.displayData.length > 0)
  }
)

const currentScheduledCourseId = ref<number | null>(null)
function setCurrentScheduledCourse(scheduledCourseId: number) {
  currentScheduledCourseId.value = scheduledCourseId
}

function fetchScheduledCurrentWeek(week: number, year: number) {
  scheduledCourseStore.fetchScheduledCourses(
    { week: week, year: year },
    { id: 1, abbrev: 'INFO', name: 'informatique' }
  )
}

function changeDate(newDate: Timestamp) {
  fetchScheduledCurrentWeek(newDate.workweek, newDate.year)
}

/**
 * Fetching data required on mount
 */
onBeforeMount(async () => {
  let todayDate = updateWorkWeek(parsed(today()) as Timestamp)
  fetchScheduledCurrentWeek(todayDate.workweek, todayDate.year)
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
