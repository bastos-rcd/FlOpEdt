import { CalendarColumn } from '@/components/calendar/declaration'
import { defineStore, storeToRefs } from 'pinia'
import { computed, ref } from 'vue'
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
  const { fetchedStructuralGroups } = storeToRefs(groupStore)
  const groupsSelected = ref<Group[]>([])

  const columns = computed(() => {
    let columns: CalendarColumn[] = []
    let max: number = 0
    fetchedStructuralGroups.value.forEach((g) => {
      if (groupsSelected.value.length !== 0) {
        groupsSelected.value.forEach((gs: Group) => {
          if (g.id === gs.id && g.columnIds.length === 1) {
            columns.push({ id: g.id, name: g.name, weight: 1 })
            if (max < g.id) max = g.id
          }
        })
      } else if (g.columnIds.length === 1) {
        columns.push({ id: g.id, name: g.name, weight: 1 })
        if (max < g.id) max = g.id
      }
    })
    columns.push({ id: max + 1, name: 'Avail', weight: 1 })
    return columns
  })

  return {
    columns,
    groupsSelected,
  }
})
