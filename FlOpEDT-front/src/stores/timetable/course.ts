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
  const tutorStore = useTutorStore()

  async function fetchScheduledCourses(week: FlopWeek, department?: Department): Promise<void> {
    isLoading.value = true
    try {
      await api.getScheduledCourses(week.week, week.year, department?.abbrev).then((result) => {
        scheduledCourses.value = result
        isLoading.value = false
        scheduledCourses.value.forEach((sc) => {
          tutorStore.fetchTutorById(sc.tutor)
          const tutorUser: User = tutorStore.getTutorById(sc.tutor) as User
          courses.value.push({
            id: sc.id,
            no: sc.course.no,
            room: {
              id: sc.room?.id as number,
              abbrev: 'ab',
              name: sc.room?.name as string,
              subroomIdOf: [],
              departmentIds: [],
            },
            start: updateWorkWeek(
              parsed(
                sc.start_time.toString().substring(0, 10) + ' ' + sc.start_time.toString().substring(11)
              ) as Timestamp
            ),
            end: updateWorkWeek(
              parsed(sc.end_time.toString().substring(0, 10) + ' ' + sc.end_time.toString().substring(11)) as Timestamp
            ),
            tutor: tutorUser,
            suppTutors: [],
            module: {
              id: -1,
              name: sc.course.module.name,
              abbrev: sc.course.module.abbrev,
              headId: -1,
              url: null,
              trainProgId: -1,
              description: 'None',
            } as Module,
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
