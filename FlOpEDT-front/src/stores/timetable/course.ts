import { api } from '@/utils/api'
import { defineStore, storeToRefs } from 'pinia'
import { ref } from 'vue'
import { ScheduledCourse, Department } from '@/ts/type'
import { Course } from '@/stores/declarations'
import { Timestamp, copyTimestamp, makeDate, nextDay, parseTime, updateFormatted } from '@quasar/quasar-ui-qcalendar'
import _ from 'lodash'
import { dateToTimestamp, getDateStringFromTimestamp, getDateTimeStringFromDate, timestampToDate } from '@/helpers'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useScheduledCourseStore = defineStore('scheduledCourse', () => {
  const scheduledCourses = ref<Map<string, ScheduledCourse[]>>(new Map<string, ScheduledCourse[]>())
  const courses = ref<Map<string, Course[]>>(new Map<string, Course[]>())
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchScheduledCourses(from?: Date, to?: Date, tutor?: number, department?: Department): Promise<void> {
    isLoading.value = true
    try {
      await api.getScheduledCourses(from, to, department?.abbrev, tutor).then((result: ScheduledCourse[]) => {
        result.forEach((r: ScheduledCourse) => {
          if (!scheduledCourses.value.has(getDateTimeStringFromDate(r.start_time, false)))
            scheduledCourses.value.set(getDateTimeStringFromDate(r.start_time, false), [])
          _.remove(scheduledCourses.value.get(getDateTimeStringFromDate(r.start_time, false))!, (sc) => sc.id === r.id)
          scheduledCourses.value.get(getDateTimeStringFromDate(r.start_time, false))?.push({
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
        scheduledCourses.value.forEach((scheduledCourses, date) => {
          if (!courses.value.has(date)) courses.value.set(date, [])
          scheduledCourses.forEach((sc) => {
            courses.value.get(date)?.push(scheduledCourseToCourse(sc))
          })
        })
      })
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  async function updateScheduledCourses(course: Course) {
    const currentDate = makeDate(course.start).toDateString()
    if (!scheduledCourses.value.has(currentDate)) {
      await fetchScheduledCourses(makeDate(course.start), makeDate(nextDay(course.start)))
      if (!scheduledCourses.value.has(currentDate)) scheduledCourses.value.set(currentDate, [])
    }
    let scheduledCourse: ScheduledCourse | undefined = scheduledCourses.value
      .get(currentDate)!
      .find((sc) => sc.id === course.id)
    if (scheduledCourse) {
      scheduledCourse.roomId = course.room
      scheduledCourse.start_time = makeDate(course.start)
      scheduledCourse.end_time = makeDate(course.end)
      scheduledCourse.tutor = course.tutorId
      scheduledCourse.suppTutorsIds = course.suppTutorIds
      scheduledCourse.groupIds = course.groupIds
      scheduledCourse.moduleId = course.module
      _.remove(scheduledCourses.value.get(currentDate)!, (sc) => sc.id === course.id)
      scheduledCourses.value.get(currentDate)!.push(scheduledCourse)
    }
    // TODO UPDATE BACK
  }

  function scheduledCourseToCourse(scheduledCourse: ScheduledCourse): Course {
    let course: Course = {
      id: scheduledCourse.id,
      no: -1,
      room: scheduledCourse.roomId,
      start: dateToTimestamp(scheduledCourse.start_time),
      end: dateToTimestamp(scheduledCourse.end_time),
      tutorId: scheduledCourse.tutor,
      suppTutorIds: _.cloneDeep(scheduledCourse.suppTutorsIds),
      module: scheduledCourse.moduleId,
      groupIds: _.cloneDeep(scheduledCourse.groupIds),
      courseTypeId: -1,
      roomTypeId: -1,
      graded: false,
      workCopy: 0,
    }
    return course
  }

  function courseToScheduledCourse(course: Course): ScheduledCourse {
    let scheduledCourse: ScheduledCourse | undefined = getScheduldedCourse(
      course.id,
      getDateStringFromTimestamp(course.start)
    )
    if (scheduledCourse) {
      scheduledCourse.roomId = course.room
      scheduledCourse.moduleId = course.module
      scheduledCourse.start_time = timestampToDate(course.start)
      scheduledCourse.end_time = timestampToDate(course.end)
      scheduledCourse.tutor = course.tutorId
      scheduledCourse.suppTutorsIds = _.cloneDeep(course.suppTutorIds)
      scheduledCourse.groupIds = _.cloneDeep(course.groupIds)
    } else {
      scheduledCourse = {
        id: course.id,
        roomId: course.room,
        start_time: timestampToDate(course.start),
        end_time: timestampToDate(course.end),
        courseId: -1,
        tutor: course.tutorId,
        id_visio: -1,
        moduleId: course.module,
        trainProgId: -1,
        groupIds: _.cloneDeep(course.groupIds),
        suppTutorsIds: _.cloneDeep(course.suppTutorIds),
      }
    }
    return scheduledCourse
  }

  function getCourse(id: number, date?: string, remove?: boolean): Course | undefined {
    let courseReturned: Course | undefined
    if (date) {
      courseReturned = courses.value.get(date)?.find((c) => c.id === id)
      if (courseReturned && remove) _.remove(courses.value.get(date)!, (c) => c.id === id)
    } else {
      courses.value.forEach((coursesD, date) => {
        const course = coursesD.find((c) => c.id === id)
        if (course) {
          courseReturned = course
          if (remove) _.remove(coursesD, (c) => c.id === id)
        }
      })
    }
    return courseReturned
  }

  function getScheduldedCourse(id: number, date?: string): ScheduledCourse | undefined {
    if (date) return scheduledCourses.value.get(date)?.find((c) => c.id === id)
    else {
      let scheduledCourse: ScheduledCourse | undefined
      scheduledCourses.value.forEach((scheduledCoursesD, date) => {
        scheduledCourse = scheduledCoursesD.find((c) => c.id === id)
        if (scheduledCourse) {
          return
        }
      })
      return scheduledCourse
    }
  }

  function getCoursesFromDates(dates: Timestamp[]): Course[] {
    const coursesReturn: Course[] = []
    dates.forEach((date) => {
      const dateString = getDateStringFromTimestamp(date)
      courses.value.get(dateString)?.forEach((c) => {
        coursesReturn.push(c)
      })
    })
    return coursesReturn
  }

  function getScheduledCoursesFromDateToDate(from: Timestamp, to?: Timestamp): ScheduledCourse[] {
    let scheduledCoursesReturn: ScheduledCourse[] = []
    if (!to)
      scheduledCourses.value.get(getDateStringFromTimestamp(from))?.forEach((c) => {
        scheduledCoursesReturn.push(c)
      })
    else {
      let currentDate = copyTimestamp(from)
      while (currentDate.weekday !== to.weekday) {
        scheduledCourses.value.get(getDateStringFromTimestamp(currentDate))?.forEach((c) => {
          scheduledCoursesReturn.push(c)
        })
        currentDate = updateFormatted(nextDay(currentDate))
      }
    }
    return scheduledCoursesReturn
  }

  function addScheduledCourseToDate(scheduledCourse: ScheduledCourse): ScheduledCourse[] {
    const dateString = getDateTimeStringFromDate(scheduledCourse.start_time, false)
    if (!scheduledCourses.value.has(dateString)) scheduledCourses.value.set(dateString, [])
    const scheduledCoursesOutput = scheduledCourses.value.get(dateString)
    scheduledCoursesOutput!.push(scheduledCourse)
    return scheduledCoursesOutput!
  }

  function addOrUpdateCourseToDate(course: Course): Course[] {
    const dateString = getDateStringFromTimestamp(course.start)
    if (!courses.value.has(dateString)) courses.value.set(dateString, [])
    const coursesOutput = courses.value.get(dateString)
    _.remove(coursesOutput!, (c) => c.id === course.id)
    coursesOutput!.push(course)
    return coursesOutput!
  }

  return {
    isLoading,
    loadingError,
    fetchScheduledCourses,
    updateScheduledCourses,
    scheduledCourseToCourse,
    courseToScheduledCourse,
    getCourse,
    getScheduldedCourse,
    getCoursesFromDates,
    getScheduledCoursesFromDateToDate,
    addScheduledCourseToDate,
    addOrUpdateCourseToDate,
    courses,
    scheduledCourses,
  }
})
