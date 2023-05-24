import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ScheduledCourse, FlopWeek, Department } from '@/ts/type'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useScheduledCourseStore = defineStore('scheduledCourse', () => {
  const scheduledCourses = ref<ScheduledCourse[]>([])
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchScheduledCourses(week: FlopWeek, department?: Department): Promise<void> {
    isLoading.value = true
    try {
      scheduledCourses.value = await api.getScheduledCourses(week.week, week.year, department?.abbrev)
    } catch (e) {
      loadingError.value = e as Error
    }
    isLoading.value = false
  }

  return {
    isLoading,
    loadingError,
    scheduledCourses,

    fetchScheduledCourses,
  }
})
