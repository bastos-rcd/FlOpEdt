import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ScheduledCourse, FlopWeek, Department } from '@/ts/type'
import { Course } from '@/stores/declarations'
import { Timestamp, makeDate, parsed, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'
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
          courses.value.push(scheduledCourseToCourse(sc))
        })
      })
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  async function updateScheduledCourses(course: Course) {
    let scheduledCourse: ScheduledCourse | undefined = scheduledCourses.value.find((sc) => sc.id === course.id)
    if (scheduledCourse) {
      scheduledCourse.course.no = course.no
      // scheduledCourse.room TODO with Roomstore
      scheduledCourse.start_time = makeDate(course.start)
      scheduledCourse.end_time = makeDate(course.end)
      scheduledCourse.tutor = course.tutorId
      // scheduledCourse.suppTutorIds TODO
      // scheduledCourse.module TODO
      // scheduledCourse.groupIds TODO with groupstore or APIcall
      // scheduledCourse.courseTypeId TODO
      // scheduledCourse.roomTypeId TODO
      scheduledCourse.course.is_graded = course.graded
      // scheduledCourse.workCopy TODO ?
      _.remove(scheduledCourses.value, (sc) => sc.id === course.id)
      scheduledCourses.value.push(scheduledCourse)
    }
    // TODO UPDATE BACK
  }

  function scheduledCourseToCourse(scheduledCourse: ScheduledCourse): Course {
    let course: Course = {
      id: scheduledCourse.id,
      no: scheduledCourse.course.no,
      room: scheduledCourse.room?.id as number,
      start: updateWorkWeek(
        parsed(
          scheduledCourse.start_time.toString().substring(0, 10) +
            ' ' +
            scheduledCourse.start_time.toString().substring(11)
        ) as Timestamp
      ),
      end: updateWorkWeek(
        parsed(
          scheduledCourse.end_time.toString().substring(0, 10) + ' ' + scheduledCourse.end_time.toString().substring(11)
        ) as Timestamp
      ),
      tutorId: scheduledCourse.tutor,
      suppTutorIds: [],
      module: -1,
      groupIds: _.map(scheduledCourse.course.groups, (gp) => gp.id),
      courseTypeId: -1,
      roomTypeId: -1,
      graded: scheduledCourse.course.is_graded,
      workCopy: 0,
    }
    return course
  }

  function courseToScheduledCourse(course: Course): ScheduledCourse | undefined {
    let scheduledCourse: ScheduledCourse | undefined = scheduledCourses.value.find((sc) => sc.id === course.id)
    if (scheduledCourse) {
      scheduledCourse.course.no = course.no
      // scheduledCourse.room TODO with Roomstore
      scheduledCourse.start_time = makeDate(course.start)
      scheduledCourse.end_time = makeDate(course.end)
      scheduledCourse.tutor = course.tutorId
      // scheduledCourse.suppTutorIds TODO
      // scheduledCourse.module TODO
      // scheduledCourse.groupIds TODO with groupstore or APIcall
      // scheduledCourse.courseTypeId TODO
      // scheduledCourse.roomTypeId TODO
      scheduledCourse.course.is_graded = course.graded
      // scheduledCourse.workCopy TODO ?
      return scheduledCourse
    } else {
      // TODO Call API to retrieve the scheduledCourse not in store
    }
  }

  return {
    isLoading,
    loadingError,
    scheduledCourses,
    courses,
    fetchScheduledCourses,
    updateScheduledCourses,
  }
})
