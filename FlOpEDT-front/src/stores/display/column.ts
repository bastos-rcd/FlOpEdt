import { CalendarColumn } from '@/components/calendar/declaration'
import { defineStore } from 'pinia'
import { computed } from 'vue'
import { useGroupStore } from '@/stores/timetable/group'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useColumnStore = defineStore('column', () => {
  const groupStore = useGroupStore()

  const columns = computed(() => {
    //const totalWeight = groups.value.filter(g => g.columnIds.length === 1).length
    let columns: CalendarColumn[] = []
    groupStore.groups.forEach((g) => {
      if (g.columnIds.length === 1) {
        columns.push({ id: g.id, name: g.name, weight: 1 })
      }
    })
    return columns
  })

  return {
    columns,
  }
})
