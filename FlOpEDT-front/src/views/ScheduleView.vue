<template>
  <Calendar
    :events="events"
    :columns="columns"
    :total-weight="8"
    @dragstart="setCurrentScheduledCourse"
    @dropevent="onDropEvent"
  />
  <button @click="revertUpdate">Revert</button>
</template>

<script setup lang="ts">

import { CalendarEvent } from '@/components/qcalendar/declaration';
import Calendar from '@/components/qcalendar/Calendar.vue'
import { computed, onBeforeMount, ref } from 'vue';
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { useGroupStore } from '@/stores/timetable/group'
import { useColumnStore } from '@/stores/display/column'
import { useUndoredo } from '@/composables/undoredo'
import { storeToRefs } from 'pinia'

const scheduledCourseStore = useScheduledCourseStore()
const groupStore = useGroupStore()
const columnStore = useColumnStore()

const { addUpdate, revertUpdate } = useUndoredo()

onBeforeMount(async () => {
  scheduledCourseStore.fetchScheduledCourses({ week: 18, year: 2023 }, { id: 1, abbrev: 'INFO', name: 'informatique'})
})
const { scheduledCourses } = storeToRefs(scheduledCourseStore)
const { groups } = storeToRefs(groupStore)
const { columns } = storeToRefs(columnStore)

const events = computed<CalendarEvent[]>(() => {
  return scheduledCourses.value.map(s => {
    const currentEvent: CalendarEvent = {
      id: s.id,
      title: s.course.type.name,
      details: '',
      date: (s.start_time as unknown as string).substring(0, 10),
      bgcolor: s.course.module.display.color_bg,
      duration: s.course.type.duration,
      time: (s.start_time as unknown as string).substring(11, 16),
      columnIds: []
    }
    s.course.groups.forEach(courseGroup => {
      const currentGroup = groups.value.find(g => g.id === courseGroup.id)
      if (currentGroup) currentEvent.columnIds?.push(...currentGroup.columnIds)
    })
    return currentEvent
  }).filter(sc => sc.columnIds?.length > 0)
})

const currentScheduledCourseId = ref<number | null>(null)
function setCurrentScheduledCourse(scheduledCourseId: number) {
  currentScheduledCourseId.value = scheduledCourseId
}

function onDropEvent(data: any) {
  addUpdate(currentScheduledCourseId.value, data)
  currentScheduledCourseId.value = null
}


</script>
