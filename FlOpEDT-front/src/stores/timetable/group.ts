import { Department, GroupAPI } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Group, User } from '@/stores/declarations'
import { api } from '@/utils/api'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useGroupStore = defineStore('group', () => {
  const isAllGroupsFetched = ref<boolean>(false)
  const fetchedGroups = ref<Group[]>([])
  const groups = ref<Group[]>([
    {
      id: 31,
      name: 'CE',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [36, 37, 38, 39, 40, 41, 42, 43],
      parentsId: [],
    },
    {
      id: 32,
      name: '1',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [36, 37],
      parentsId: [31],
    },
    {
      id: 33,
      name: '2',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [38, 39],
      parentsId: [31],
    },
    {
      id: 34,
      name: '3',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [40, 41],
      parentsId: [31],
    },
    {
      id: 35,
      name: '4',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [42, 43],
      parentsId: [31],
    },
    {
      id: 36,
      name: '1A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [36],
      parentsId: [32],
    },
    {
      id: 37,
      name: '1B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [37],
      parentsId: [32],
    },
    {
      id: 38,
      name: '2A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [38],
      parentsId: [33],
    },
    {
      id: 39,
      name: '2B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [39],
      parentsId: [33],
    },
    {
      id: 40,
      name: '3A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [40],
      parentsId: [34],
    },
    {
      id: 41,
      name: '3B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [41],
      parentsId: [34],
    },
    {
      id: 42,
      name: '4A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [42],
      parentsId: [35],
    },
    {
      id: 43,
      name: '4B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [43],
      parentsId: [35],
    },
  ])

  async function fetchGroups(department: Department): Promise<void> {
    clearGroups()
    await api.getStructuralGroups(department.abbrev).then((result: GroupAPI[]) => {
      result.forEach((gp: GroupAPI) => {
        let newGp = {
          id: gp.id,
          name: gp.name,
          size: 0,
          trainProgId: -1,
          type: 'structural',
          parentsId: gp.parent_ids,
          columnIds: [],
        } as Group
        fetchedGroups.value.push(newGp)
      })
      isAllGroupsFetched.value = true
    })
    fetchedGroups.value = populateGroupsColumnIds(fetchedGroups.value)
  }

  function clearGroups(): void {
    fetchedGroups.value = []
  }

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

    // Recursive function to collect all descendant leaf node IDs
    function collectDescendantLeafNodeIds(groupId: number): number[] {
      const children = childrenMap.get(groupId)
      if (!children || children.length === 0) {
        return [groupId] // Leaf node
      }
      // Collect leaf node IDs from all children recursively
      return children.flatMap((childId) => collectDescendantLeafNodeIds(childId))
    }

    // Generate columnIds for each group
    return groups.map((group) => {
      const descendantLeafNodeIds = collectDescendantLeafNodeIds(group.id)
      return { ...group, columnIds: descendantLeafNodeIds }
    })
  }

  return {
    groups,
    fetchedGroups,
    fetchGroups,
  }
})
