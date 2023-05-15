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
      id: 18,
      name: 'CE',
      columnIds: [422, 24, 25, 26, 27, 28, 29, 30],
      parentId: null
    },
    {
      id: 19,
      name: '1',
      columnIds: [422, 24],
      parentId: 18
    },
    {
      id: 20,
      name: '2',
      columnIds: [25, 26],
      parentId: 18
    },
    {
      id: 21,
      name: '3',
      columnIds: [27, 28],
      parentId: 18
    },
    {
      id: 22,
      name: '4',
      columnIds: [29, 30],
      parentId: 18
    },
    {
      id: 422,
      name: 'BUT1',
      columnIds: [422],
      parentId: 19
    },
    {
      id: 24,
      name: '1B',
      columnIds: [24],
      parentId: 19
    },
    {
      id: 25,
      name: '2A',
      columnIds: [25],
      parentId: 20
    },
    {
      id: 26,
      name: '2B',
      columnIds: [26],
      parentId: 20
    },
    {
      id: 27,
      name: '3A',
      columnIds: [27],
      parentId: 21
    },
    {
      id: 28,
      name: '3B',
      columnIds: [28],
      parentId: 21
    },
    {
      id: 29,
      name: '4A',
      columnIds: [29],
      parentId: 22
    },
    {
      id: 30,
      name: '4B',
      columnIds: [30],
      parentId: 22
    },
  ])

  return {
    groups,
  }
})
