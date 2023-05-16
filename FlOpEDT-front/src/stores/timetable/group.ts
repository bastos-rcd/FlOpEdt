import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useGroupStore = defineStore('group', () => {
  const groups = ref([
    {
      id: 419,
      name: 'CE',
      columnIds: [424, 425, 426, 427, 428, 429, 430, 431],
      parentId: null,
    },
    {
      id: 420,
      name: '1',
      columnIds: [424, 425],
      parentId: 419,
    },
    {
      id: 421,
      name: '2',
      columnIds: [426, 427],
      parentId: 419,
    },
    {
      id: 422,
      name: '3',
      columnIds: [428, 429],
      parentId: 419,
    },
    {
      id: 423,
      name: '4',
      columnIds: [430, 431],
      parentId: 419,
    },
    {
      id: 424,
      name: '1A',
      columnIds: [424],
      parentId: 420,
    },
    {
      id: 425,
      name: '1B',
      columnIds: [425],
      parentId: 420,
    },
    {
      id: 426,
      name: '2A',
      columnIds: [426],
      parentId: 421,
    },
    {
      id: 427,
      name: '2B',
      columnIds: [427],
      parentId: 421,
    },
    {
      id: 428,
      name: '3A',
      columnIds: [428],
      parentId: 422,
    },
    {
      id: 429,
      name: '3B',
      columnIds: [429],
      parentId: 422,
    },
    {
      id: 430,
      name: '4A',
      columnIds: [430],
      parentId: 423,
    },
    {
      id: 431,
      name: '4B',
      columnIds: [431],
      parentId: 423,
    },
  ])

  return {
    groups,
  }
})
