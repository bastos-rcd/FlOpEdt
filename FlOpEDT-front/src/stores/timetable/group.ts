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
      id: 419,
      name: 'CE',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [424, 425, 426, 427, 428, 429, 430, 431],
      parentsId: [],
    },
    {
      id: 420,
      name: '1',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [424, 425],
      parentsId: [419],
    },
    {
      id: 421,
      name: '2',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [426, 427],
      parentsId: [419],
    },
    {
      id: 422,
      name: '3',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [428, 429],
      parentsId: [419],
    },
    {
      id: 423,
      name: '4',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [430, 431],
      parentsId: [419],
    },
    {
      id: 424,
      name: '1A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [424],
      parentsId: [420],
    },
    {
      id: 425,
      name: '1B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [425],
      parentsId: [420],
    },
    {
      id: 426,
      name: '2A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [426],
      parentsId: [421],
    },
    {
      id: 427,
      name: '2B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [427],
      parentsId: [421],
    },
    {
      id: 428,
      name: '3A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [428],
      parentsId: [422],
    },
    {
      id: 429,
      name: '3B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [429],
      parentsId: [422],
    },
    {
      id: 430,
      name: '4A',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [430],
      parentsId: [423],
    },
    {
      id: 431,
      name: '4B',
      size: 1,
      trainProgId: -1,
      type: 'structural',
      columnIds: [431],
      parentsId: [423],
    },
  ])

  async function fetchGroups(department: Department): Promise<void> {
    await api.getGroups().then((result: GroupAPI[]) => {
      result.forEach((gp: GroupAPI) => {
        fetchedGroups.value.push({
          id: gp.id,
          name: gp.name,
          size: 0,
          trainProgId: -1,
          type: 'structural', // structural or transversal
          parentsId: [],
          columnIds: [],
        })
      })
      isAllGroupsFetched.value = true
    })
  }

  return {
    groups,
    fetchedGroups,
    fetchGroups,
  }
})
