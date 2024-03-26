import { CalendarColumn } from '@/components/calendar/declaration'
import { defineStore, storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useGroupStore } from '@/stores/timetable/group'
import { Group } from '../declarations'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useColumnStore = defineStore('column', () => {
  const groupStore = useGroupStore()
  const { fetchedStructuralGroups, groups } = storeToRefs(groupStore)
  const max = computed((): number => {
    let currentMax: number = 0
    fetchedStructuralGroups.value.forEach((g: Group) => {
      if (g.columnIds.length === 1) {
        if (currentMax < g.id) currentMax = g.id
      }
    })
    return currentMax
  })
  const columns = computed(() => {
    const columns: CalendarColumn[] = []
    groups.value.forEach((g: Group) => {
      if (g.type === 'structural' && g.columnIds.length === 1) {
        columns.push({ id: g.id, name: g.name, weight: 1 })
      }
    })
    columns.push({ id: max.value + 1, name: 'Avail', weight: 1 })
    return columns
  })

  return {
    columns,
  }
})
