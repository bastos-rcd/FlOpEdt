import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ScheduledCourse, FlopWeek, Department } from '@/ts/type'
import { Course, Module, User } from '@/stores/declarations'
import { Timestamp, parsed, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'
import { useTutorStore } from './tutor'
import _ from 'lodash'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useScheduledCourseStore = defineStore('scheduledCourse', () => {
  const scheduledCourses = ref<ScheduledCourse[]>([])
  const courses = ref<Course[]>([])
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchScheduledCourses(week: FlopWeek, department?: Department): Promise<void> {
    isLoading.value = true
    try {
      await api.getScheduledCourses(week.week, week.year, department?.abbrev).then((result) => {
        scheduledCourses.value = result
        isLoading.value = false
        scheduledCourses.value.forEach((sc) => {
          courses.value.push({
            id: sc.id,
            no: sc.course.no,
            room: sc.room?.id as number,
            start: updateWorkWeek(
              parsed(
                sc.start_time.toString().substring(0, 10) + ' ' + sc.start_time.toString().substring(11)
              ) as Timestamp
            ),
            end: updateWorkWeek(
              parsed(sc.end_time.toString().substring(0, 10) + ' ' + sc.end_time.toString().substring(11)) as Timestamp
            ),
            tutor: sc.tutor,
            suppTutors: [],
            module: -1,
            groupIds: _.map(sc.course.groups, (gp) => gp.id),
            courseTypeId: -1,
            roomTypeId: -1,
            graded: sc.course.is_graded,
            workCopy: 0,
          })
        })
      })
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  return {
    isLoading,
    loadingError,
    scheduledCourses,
    courses,
    fetchScheduledCourses,
  }
})
