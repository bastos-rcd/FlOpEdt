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
      parentsId: [],
    },
    {
      id: 420,
      name: '1',
      columnIds: [424, 425],
      parentsId: [419],
    },
    {
      id: 421,
      name: '2',
      columnIds: [426, 427],
      parentsId: [419],
    },
    {
      id: 422,
      name: '3',
      columnIds: [428, 429],
      parentsId: [419],
    },
    {
      id: 423,
      name: '4',
      columnIds: [430, 431],
      parentsId: [419],
    },
    {
      id: 424,
      name: '1A',
      columnIds: [424],
      parentsId: [420],
    },
    {
      id: 425,
      name: '1B',
      columnIds: [425],
      parentsId: [420],
    },
    {
      id: 426,
      name: '2A',
      columnIds: [426],
      parentsId: [421],
    },
    {
      id: 427,
      name: '2B',
      columnIds: [427],
      parentsId: [421],
    },
    {
      id: 428,
      name: '3A',
      columnIds: [428],
      parentsId: [422],
    },
    {
      id: 429,
      name: '3B',
      columnIds: [429],
      parentsId: [422],
    },
    {
      id: 430,
      name: '4A',
      columnIds: [430],
      parentsId: [423],
    },
    {
      id: 431,
      name: '4B',
      columnIds: [431],
      parentsId: [423],
    },
  ])

  return {
    groups,
  }
})
