import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ScheduledCourse, Department } from '@/ts/type'
import { Course as CourseFront } from '@/stores/declarations'
import { makeDate } from '@quasar/quasar-ui-qcalendar'
import _ from 'lodash'
import { dateToTimestamp } from '@/helpers'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useScheduledCourseStore = defineStore('scheduledCourse', () => {
  const scheduledCourses = ref<ScheduledCourse[]>([])
  const courses = ref<CourseFront[]>([])
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchScheduledCourses(from?: Date, to?: Date, tutor?: number, department?: Department): Promise<void> {
    isLoading.value = true
    try {
      await api.getScheduledCourses(from, to, department?.abbrev, tutor).then((result: ScheduledCourse[]) => {
        result.forEach((r: ScheduledCourse) => {
          scheduledCourses.value.push({
            id: r.id,
            roomId: r.roomId,
            start_time: new Date(r.start_time),
            end_time: new Date(r.end_time),
            courseId: r.courseId,
            tutor: r.tutor,
            id_visio: -1,
            moduleId: r.moduleId,
            trainProgId: r.trainProgId,
            groupIds: r.groupIds,
            suppTutorsIds: r.suppTutorsIds,
          })
        })
        isLoading.value = false
        scheduledCourses.value.forEach((sc) => {
          courses.value.push(scheduledCourseToCourse(sc))
        })
      })
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  async function updateScheduledCourses(course: CourseFront) {
    let scheduledCourse: ScheduledCourse | undefined = scheduledCourses.value.find((sc) => sc.id === course.id)
    if (scheduledCourse) {
      scheduledCourse.roomId = course.room
      scheduledCourse.start_time = makeDate(course.start)
      scheduledCourse.end_time = makeDate(course.end)
      scheduledCourse.tutor = course.tutorId
      scheduledCourse.suppTutorsIds = course.suppTutorIds
      scheduledCourse.groupIds = course.groupIds
      scheduledCourse.moduleId = course.module
      _.remove(scheduledCourses.value, (sc) => sc.id === course.id)
      scheduledCourses.value.push(scheduledCourse)
    }
    // TODO UPDATE BACK
  }

  function scheduledCourseToCourse(scheduledCourse: ScheduledCourse): CourseFront {
    let course: CourseFront = {
      id: scheduledCourse.id,
      no: -1,
      room: scheduledCourse.roomId,
      start: dateToTimestamp(scheduledCourse.start_time),
      end: dateToTimestamp(scheduledCourse.end_time),
      tutorId: scheduledCourse.tutor,
      suppTutorIds: [],
      module: scheduledCourse.moduleId,
      groupIds: [],
      courseTypeId: -1,
      roomTypeId: -1,
      graded: false,
      workCopy: 0,
    }
    scheduledCourse.suppTutorsIds?.forEach((sti) => {
      course.suppTutorIds.push(sti)
    })
    scheduledCourse.groupIds?.forEach((gId) => {
      course.groupIds.push(gId)
    })
    return course
  }

  function courseToScheduledCourse(course: CourseFront): ScheduledCourse {
    let scheduledCourse: ScheduledCourse | undefined = scheduledCourses.value.find((sc) => sc.id === course.id)
    if (scheduledCourse) {
      scheduledCourse.roomId = course.room
      scheduledCourse.moduleId = course.module
      scheduledCourse.start_time = makeDate(course.start)
      scheduledCourse.end_time = makeDate(course.end)
      scheduledCourse.tutor = course.tutorId
      course.suppTutorIds.forEach((id) => scheduledCourse!.suppTutorsIds.push(id))
      course.groupIds.forEach((id) => scheduledCourse!.groupIds.push(id))
    } else {
      scheduledCourse = {
        id: course.id,
        roomId: course.room,
        start_time: makeDate(course.start),
        end_time: makeDate(course.end),
        courseId: -1,
        tutor: course.tutorId,
        id_visio: -1,
        moduleId: course.module,
        trainProgId: -1,
        groupIds: course.groupIds,
        suppTutorsIds: course.suppTutorIds,
      }
    }
    return scheduledCourse
  }

  return {
    isLoading,
    loadingError,
    scheduledCourses,
    courses,
    fetchScheduledCourses,
    updateScheduledCourses,
    scheduledCourseToCourse,
    courseToScheduledCourse,
  }
})
