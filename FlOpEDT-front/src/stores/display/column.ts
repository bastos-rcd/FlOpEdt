import { CalendarColumn } from '@/components/qcalendar/declaration'
import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useColumnStore = defineStore('column', () => {

  const columns = ref<CalendarColumn[]>([
    {
      id: 23,
      name: '1A',
      weight: 1,
      x: 0,
    },
    {
      id: 24,
      name: '1B',
      weight: 1,
      x: 1,
    },
    {
      id: 25,
      name: '2A',
      weight: 1,
      x: 2,
    },
    {
      id: 26,
      name: '2B',
      weight: 1,
      x: 3,
    },
    {
      id: 27,
      name: '3A',
      weight: 1,
      x: 4,
    },
    {
      id: 28,
      name: '3B',
      weight: 1,
      x: 5,
    },
    {
      id: 29,
      name: '4A',
      weight: 1,
      x: 6,
    },
    {
      id: 30,
      name: '4B',
      weight: 1,
      x: 7,
    },
    /*     {
        "id": 36,
        "name": "1A",
        "weight": 1,
        "x": 8
    },
    {
        "id": 37,
        "name": "1B",
        "weight": 1,
        "x": 9
    },
    {
        "id": 38,
        "name": "2A",
        "weight": 1,
        "x": 10
    },
    {
        "id": 39,
        "name": "2B",
        "weight": 1,
        "x": 11
    },
    {
        "id": 40,
        "name": "3A",
        "weight": 1,
        "x": 12
    },
    {
        "id": 41,
        "name": "3B",
        "weight": 1,
        "x": 13
    },
    {
        "id": 35,
        "name": "4",
        "weight": 1,
        "x": 14
    },
    {
        "id": 43,
        "name": "LP",
        "weight": 1,
        "x": 15
    } */
  ])

  return {
    columns,
  }
})
