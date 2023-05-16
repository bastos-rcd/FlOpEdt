import { CalendarColumn } from '@/components/calendar/declaration'
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
      id: 424,
      name: '1A',
      weight: 1,
    },
    {
      id: 425,
      name: '1B',
      weight: 1,
    },
    {
      id: 426,
      name: '2A',
      weight: 1,
    },
    {
      id: 427,
      name: '2B',
      weight: 1,
    },
    {
      id: 428,
      name: '3A',
      weight: 1,
    },
    {
      id: 429,
      name: '3B',
      weight: 1,
    },
    {
      id: 430,
      name: '4A',
      weight: 1,
    },
    {
      id: 431,
      name: '4B',
      weight: 1,
    },
  ])

  return {
    columns,
  }
})
