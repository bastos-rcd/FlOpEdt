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
      columnIds: [23, 24, 25, 26, 27, 28, 29, 30],
    },
    {
      id: 19,
      name: '1',
      columnIds: [23, 24],
    },
    {
      id: 20,
      name: '2',
      columnIds: [25, 26],
    },
    {
      id: 21,
      name: '3',
      columnIds: [27, 28],
    },
    {
      id: 22,
      name: '4',
      columnIds: [29, 30],
    },
    {
      id: 422,
      name: 'BUT1',
      columnIds: [422],
    },
    {
      id: 24,
      name: '1B',
      columnIds: [24],
    },
    {
      id: 25,
      name: '2A',
      columnIds: [25],
    },
    {
      id: 26,
      name: '2B',
      columnIds: [26],
    },
    {
      id: 27,
      name: '3A',
      columnIds: [27],
    },
    {
      id: 28,
      name: '3B',
      columnIds: [28],
    },
    {
      id: 29,
      name: '4A',
      columnIds: [29],
    },
    {
      id: 30,
      name: '4B',
      columnIds: [30],
    },
    {
      id: 31,
      name: 'CE',
      columnIds: [36, 37, 38, 39, 40, 41, 35],
    },
    {
      id: 32,
      name: '1',
      columnIds: [36, 37],
    },
    {
      id: 33,
      name: '2',
      columnIds: [38, 39],
    },
    {
      id: 34,
      name: '3',
      columnIds: [40, 41],
    },
    {
      id: 35,
      name: '4',
      columnIds: [35],
    },
    {
      id: 36,
      name: '1A',
      columnIds: [36],
    },
    {
      id: 37,
      name: '1B',
      columnIds: [37],
    },
    {
      id: 38,
      name: '2A',
      columnIds: [38],
    },
    {
      id: 39,
      name: '2B',
      columnIds: [39],
    },
    {
      id: 40,
      name: '3A',
      columnIds: [40],
    },
    {
      id: 41,
      name: '3B',
      columnIds: [41],
    },
    {
      id: 42,
      name: '234',
      columnIds: [38, 39, 40, 41, 35],
    },
    {
      id: 43,
      name: 'LP',
      columnIds: [43],
    },
  ])

  return {
    groups,
  }
})
