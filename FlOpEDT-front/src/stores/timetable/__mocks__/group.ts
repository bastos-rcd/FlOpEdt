import { Department } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Group } from '@/stores/declarations'
import _ from 'lodash'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useGroupStore = defineStore('group', () => {
  const fetchedTransversalGroups = ref<Group[]>([
    {
      id: 13,
      name: 'Anglais 1',
      size: 110,
      trainProgId: 101,
      type: 'transversal',
      parentsId: [],
      conflictingGroupIds: [2, 7],
      parallelGroupIds: [16, 17],
      columnIds: [],
    },
    {
      id: 14,
      name: 'Anglais 2',
      size: 115,
      trainProgId: 101,
      type: 'transversal',
      parentsId: [],
      conflictingGroupIds: [8, 9, 10],
      parallelGroupIds: [16, 17],
      columnIds: [],
    },
    {
      id: 15,
      name: 'Anglais 3',
      size: 120,
      trainProgId: 101,
      type: 'transversal',
      parentsId: [],
      conflictingGroupIds: [11, 12],
      parallelGroupIds: [18],
      columnIds: [],
    },
    {
      id: 16,
      name: 'Allemand 1',
      size: 125,
      trainProgId: 101,
      type: 'transversal',
      parentsId: [],
      conflictingGroupIds: [2, 3],
      parallelGroupIds: [13, 14, 17],
      columnIds: [],
    },
    {
      id: 17,
      name: 'Allemand 2',
      size: 130,
      trainProgId: 101,
      type: 'transversal',
      parentsId: [],
      conflictingGroupIds: [2, 3],
      parallelGroupIds: [13, 14, 16],
      columnIds: [],
    },
    {
      id: 18,
      name: 'Quechua 1',
      size: 135,
      trainProgId: 101,
      type: 'transversal',
      parentsId: [],
      conflictingGroupIds: [12],
      parallelGroupIds: [15],
      columnIds: [],
    },
  ])
  const fetchedStructuralGroups = ref<Group[]>([
    {
      id: 1,
      name: 'CE',
      size: 50,
      trainProgId: 101,
      type: 'structural',
      parentsId: [],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 2,
      name: 'TDA',
      size: 55,
      trainProgId: 101,
      type: 'structural',
      parentsId: [1],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 3,
      name: 'TDB',
      size: 60,
      trainProgId: 101,
      type: 'structural',
      parentsId: [1],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 4,
      name: 'TDC',
      size: 65,
      trainProgId: 101,
      type: 'structural',
      parentsId: [1],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 5,
      name: 'TPA1',
      size: 70,
      trainProgId: 101,
      type: 'structural',
      parentsId: [2],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 6,
      name: 'TPA2',
      size: 75,
      trainProgId: 101,
      type: 'structural',
      parentsId: [2],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 7,
      name: 'TPB1',
      size: 80,
      trainProgId: 101,
      type: 'structural',
      parentsId: [3],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 8,
      name: 'TPB2',
      size: 85,
      trainProgId: 101,
      type: 'structural',
      parentsId: [3],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 9,
      name: 'TPB3',
      size: 90,
      trainProgId: 101,
      type: 'structural',
      parentsId: [3],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 10,
      name: 'TPC1',
      size: 95,
      trainProgId: 101,
      type: 'structural',
      parentsId: [4],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 11,
      name: 'TPC2',
      size: 100,
      trainProgId: 101,
      type: 'structural',
      parentsId: [4],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
    {
      id: 12,
      name: 'TPC3',
      size: 105,
      trainProgId: 101,
      type: 'structural',
      parentsId: [4],
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [],
    },
  ])
  const groups = ref<Group[]>([
    {
      id: 31,
      name: 'CE',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [36, 37, 38, 39, 40, 41, 42, 43],
      parentsId: [],
    },
    {
      id: 32,
      name: '1',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [36, 37],
      parentsId: [31],
    },
    {
      id: 33,
      name: '2',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [38, 39],
      parentsId: [31],
    },
    {
      id: 34,
      name: '3',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [40, 41],
      parentsId: [31],
    },
    {
      id: 35,
      name: '4',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [42, 43],
      parentsId: [31],
    },
    {
      id: 36,
      name: '1A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [36],
      parentsId: [32],
    },
    {
      id: 37,
      name: '1B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [37],
      parentsId: [32],
    },
    {
      id: 38,
      name: '2A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [38],
      parentsId: [33],
    },
    {
      id: 39,
      name: '2B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [39],
      parentsId: [33],
    },
    {
      id: 40,
      name: '3A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [40],
      parentsId: [34],
    },
    {
      id: 41,
      name: '3B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [41],
      parentsId: [34],
    },
    {
      id: 42,
      name: '4A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [42],
      parentsId: [35],
    },
    {
      id: 43,
      name: '4B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      conflictingGroupIds: [],
      parallelGroupIds: [],
      columnIds: [43],
      parentsId: [35],
    },
  ])

  async function fetchGroups(department: Department): Promise<void> {
    fetchedStructuralGroups.value = populateGroupsColumnIds(fetchedStructuralGroups.value)
    populateTransversalsColumnIds(fetchedTransversalGroups.value, fetchedStructuralGroups.value)
    groups.value = _.concat(fetchedStructuralGroups.value, fetchedTransversalGroups.value)
  }

  function clearGroups(): void {}

  function populateTransversalsColumnIds(groups: Group[], structurals: Group[]): void {
    groups.forEach((gp: Group) => {
      gp.conflictingGroupIds.forEach((cgId: number) => {
        const conflictingGroup: Group | undefined = structurals.find((gpConf) => gpConf.id === cgId)
        if (conflictingGroup) {
          conflictingGroup.columnIds.forEach((id) => gp.columnIds.push(id))
        }
      })
    })
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
    fetchedStructuralGroups,
    fetchedTransversalGroups,
    fetchGroups,
    populateGroupsColumnIds,
    populateTransversalsColumnIds,
  }
})
