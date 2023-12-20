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
  const { fetchedGroups } = storeToRefs(groupStore)

  const columns = computed(() => {
    //const totalWeight = groups.value.filter(g => g.columnIds.length === 1).length
    let columns: CalendarColumn[] = []
    const groupsWithColumns = populateGroupsColumnIds(fetchedGroups.value)
    console.log('groups: ', fetchedGroups.value)
    console.log('transformed: ', groupsWithColumns)
    let max: number = 0
    groupsWithColumns.forEach((g) => {
      if (g.columnIds.length === 1) {
        columns.push({ id: g.id, name: g.name, weight: 1 })
        if (max < g.id) max = g.id
      }
    })
    columns.push({ id: max + 1, name: 'Avail', weight: 1 })
    return columns
  })

  function populateGroupsColumnIds(groups: Group[]): Group[] {
    // Map to keep track of children for each group
    const childrenMap = new Map<number, number[]>()

    // Initialize the map with empty arrays for each group
    groups.forEach((group) => {
      childrenMap.set(group.id, [])
    })

    // Populate the map with children IDs
    groups.forEach((group) => {
      if (group.parentsId) {
        group.parentsId.forEach((parentId) => {
          const children = childrenMap.get(parentId)
          if (children) {
            children.push(group.id)
          }
        })
      }
    })
    // Generate columnIds for each group
    return groups.map((group) => {
      const children = childrenMap.get(group.id)
      if (children && children.length > 0) {
        return { ...group, columnIds: children }
      } else {
        // For groups with no children, columnIds will contain only their own ID
        return { ...group, columnIds: [group.id] }
      }
    })
  }

  return {
    columns,
  }
})
