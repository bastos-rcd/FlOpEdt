import { Department, GroupAPI } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Group } from '@/stores/declarations'
import { api } from '@/utils/api'
import _ from 'lodash'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useGroupStore = defineStore('group', () => {
  const isAllGroupsFetched = ref<boolean>(false)
  const fetchedTransversalGroups = ref<Group[]>([])
  const fetchedStructuralGroups = ref<Group[]>([])
  const groups = ref<Group[]>([])

  async function fetchGroups(department: Department): Promise<void> {
    clearGroups()
    await api.getStructuralGroups(department.abbrev).then((result: GroupAPI[]) => {
      result.forEach((gp: GroupAPI) => {
        let newGp = {
          id: gp.id,
          name: gp.name,
          size: 0,
          trainProgId: gp.train_prog_id,
          type: 'structural',
          parentsId: gp.parent_ids,
          conflictingGroupIds: [],
          parallelGroupIds: [],
          columnIds: [],
        } as Group
        fetchedStructuralGroups.value.push(newGp)
      })
    })
    fetchedStructuralGroups.value = populateGroupsColumnIds(fetchedStructuralGroups.value)

    await api.getTransversalGroups(department.abbrev).then((result: GroupAPI[]) => {
      result.forEach((gp: GroupAPI) => {
        let newGp = {
          id: gp.id,
          name: gp.name,
          size: 0,
          trainProgId: gp.train_prog_id,
          type: 'transversal',
          columnIds: [],
          parentsId: [],
          conflictingGroupIds: gp.conflicting_group_ids,
          parallelGroupIds: gp.parallel_group_ids,
        } as Group
        fetchedTransversalGroups.value.push(newGp)
      })
      populateTransversalsColumnIds(fetchedTransversalGroups.value, fetchedStructuralGroups.value)
      groups.value = _.concat(fetchedStructuralGroups.value, fetchedTransversalGroups.value)
      isAllGroupsFetched.value = true
    })
  }

  function clearGroups(): void {
    fetchedStructuralGroups.value = []
    fetchedTransversalGroups.value = []
  }

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
  }
})
