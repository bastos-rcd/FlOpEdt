<template>
  <Calendar
    v-model:events="calendarEvents"
    :columns="columns"
    @dragstart="setCurrentScheduledCourse"
    @update:week="changeDate"
  />
  <button @click="revertUpdate">Revert</button>
</template>

<script setup lang="ts">
import { CalendarEvent } from '@/components/calendar/declaration'
import Calendar from '@/components/calendar/Calendar.vue'
import { onBeforeMount, ref, watch } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { useGroupStore } from '@/stores/timetable/group'
import { useColumnStore } from '@/stores/display/column'
import { useUndoredo } from '@/composables/undoredo'
import { storeToRefs } from 'pinia'
import { parsed } from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'
import { Timestamp, today, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'


const scheduledCourseStore = useScheduledCourseStore()
const groupStore = useGroupStore()
const columnStore = useColumnStore()
const calendarEvents = ref<CalendarEvent[]>([])

const { addUpdate, revertUpdate } = useUndoredo()

onBeforeMount(async () => {
  let todayDate = updateWorkWeek(parsed(today()) as Timestamp)
  fetchScheduledCurrentWeek(todayDate.workweek, todayDate.year)
  
})
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
          title: s.course.type.name,
          details: '',
          bgcolor: s.course.module.display.color_bg,
          columnIds: [],
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
            currentEvent.columnIds.push(...currentGroup.columnIds)
          }
        })
        return currentEvent
      })
      .filter((sc) => sc.columnIds.length > 0)
  }
)

const currentScheduledCourseId = ref<number | null>(null)
function setCurrentScheduledCourse(scheduledCourseId: number) {
  currentScheduledCourseId.value = scheduledCourseId
}

function changeDate(newDate: Timestamp) {
  fetchScheduledCurrentWeek(newDate.workweek, newDate.year)
}

function fetchScheduledCurrentWeek(week: number, year: number) {
  scheduledCourseStore.fetchScheduledCourses(
    { week: week, year: year },
    { id: 1, abbrev: 'INFO', name: 'informatique' }
  )
}
</script>

<style scoped></style>
