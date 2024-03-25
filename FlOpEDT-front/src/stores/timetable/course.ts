import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { ScheduledCourse, Department } from '@/ts/type'
import { Course } from '@/stores/declarations'
import {
  Timestamp,
  copyTimestamp,
  makeDate,
  nextDay,
  parseTimestamp,
  today,
  updateFormatted,
} from '@quasar/quasar-ui-qcalendar'
import { remove, cloneDeep } from 'lodash'
import { getDateStringFromTimestamp, getDateTimeStringFromDate } from '@/helpers'

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
  const courseTypeIds = ref<{ id: number; name: string }[]>([])
  const courseTypeColors = computed(() => {
    const courseTypeColors: Map<number, string> = new Map<number, string>()
    courseTypeIds.value.forEach((ct: { id: number; name: string }) => {
      const colorValue =
        'rgb(' +
        Math.ceil(Math.random() * 155) +
        ',' +
        Math.ceil(Math.random() * 155) +
        ',' +
        Math.ceil(Math.random() * 155) +
        ')'
      courseTypeColors.set(ct.id, colorValue)
    })
    return courseTypeColors
  })

  async function fetchScheduledCourses(from?: Date, to?: Date, tutor?: number, department?: Department): Promise<void> {
    //gérer les cours déjà fetched précédemment pour ne pas avoir à tout récupérer à nouveau
    scheduledCourses.value = new Map<string, ScheduledCourse[]>()
    courses.value = new Map<string, Course[]>()
    if (scheduledCourses.value.has(getDateTimeStringFromDate(from!))) isLoading.value = true
    try {
      await api.getScheduledCourses(from, to, department?.id, tutor).then((result: ScheduledCourse[]) => {
        result.forEach((r: ScheduledCourse) => {
          if (r.start_time) {
            if (!scheduledCourses.value.has(getDateStringFromTimestamp(r.start_time)))
              scheduledCourses.value.set(getDateStringFromTimestamp(r.start_time), [])
            remove(scheduledCourses.value.get(getDateStringFromTimestamp(r.start_time))!, (sc) => sc.id === r.id)
            scheduledCourses.value.get(getDateStringFromTimestamp(r.start_time))?.push({
              id: r.id,
              roomId: r.roomId,
              start_time: r.start_time,
              end_time: r.end_time,
              courseId: r.courseId,
              tutor: r.tutor,
              id_visio: -1,
              moduleId: r.moduleId,
              trainProgId: r.trainProgId,
              groupIds: r.groupIds,
              suppTutorsIds: r.suppTutorsIds,
              no: r.no,
              courseTypeId: r.courseTypeId,
            })
            if (!courseTypeIds.value.map((ct) => ct.id).includes(r.courseTypeId)) {
              courseTypeIds.value.push({ id: r.courseTypeId, name: '' })
            }
          }
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
    const scheduledCourse: ScheduledCourse | undefined = scheduledCourses.value
      .get(currentDate)!
      .find((sc) => sc.id === course.id)
    if (scheduledCourse) {
      scheduledCourse.roomId = course.room
      scheduledCourse.start_time = course.start
      scheduledCourse.end_time = course.end
      scheduledCourse.tutor = course.tutorId
      scheduledCourse.suppTutorsIds = course.suppTutorIds
      scheduledCourse.groupIds = course.groupIds
      scheduledCourse.moduleId = course.module
      remove(scheduledCourses.value.get(currentDate)!, (sc) => sc.id === course.id)
      scheduledCourses.value.get(currentDate)!.push(scheduledCourse)
    }
    // TODO UPDATE BACK
  }

  function scheduledCourseToCourse(scheduledCourse: ScheduledCourse): Course {
    const course: Course = {
      id: scheduledCourse.id,
      no: scheduledCourse.no,
      room: scheduledCourse.roomId,
      start: parseTimestamp(today())!,
      end: parseTimestamp(today())!,
      tutorId: scheduledCourse.tutor,
      suppTutorIds: cloneDeep(scheduledCourse.suppTutorsIds),
      module: scheduledCourse.moduleId,
      groupIds: cloneDeep(scheduledCourse.groupIds),
      courseTypeId: scheduledCourse.courseTypeId,
      roomTypeId: -1,
      graded: false,
      workCopy: 0,
    }
    if (scheduledCourse.start_time && scheduledCourse.end_time) {
      course.start = scheduledCourse.start_time
      course.end = scheduledCourse.end_time
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
      scheduledCourse.start_time = course.start
      scheduledCourse.end_time = course.end
      scheduledCourse.tutor = course.tutorId
      scheduledCourse.suppTutorsIds = cloneDeep(course.suppTutorIds)
      scheduledCourse.groupIds = cloneDeep(course.groupIds)
    } else {
      scheduledCourse = {
        id: course.id,
        roomId: course.room,
        start_time: course.start,
        end_time: course.end,
        courseId: -1,
        tutor: course.tutorId,
        id_visio: -1,
        moduleId: course.module,
        trainProgId: -1,
        groupIds: cloneDeep(course.groupIds),
        suppTutorsIds: cloneDeep(course.suppTutorIds),
        no: -1,
        courseTypeId: -1,
      }
    }
    return scheduledCourse
  }

  function getCourse(id: number, date?: string, removed: boolean = false): Course | undefined {
    let courseReturned: Course | undefined
    if (date) {
      courseReturned = courses.value.get(date)?.find((c) => c.id === id)
      if (courseReturned && removed) remove(courses.value.get(date)!, (c) => c.id === id)
    } else {
      courses.value.forEach((coursesD) => {
        const course = coursesD.find((c) => c.id === id)
        if (course) {
          courseReturned = course
          if (removed) remove(coursesD, (c) => c.id === id)
        }
      })
    }
    return courseReturned
  }

  function removeCourse(id: number, date?: string): void {
    if (date) {
      const coursesToDate = courses.value.get(date)
      if (coursesToDate) remove(coursesToDate, (c) => c.id === id)
    } else {
      courses.value.forEach((coursesD) => {
        remove(coursesD, (c) => c.id === id)
      })
    }
  }

  function getScheduldedCourse(id: number, date?: string): ScheduledCourse | undefined {
    if (date) return scheduledCourses.value.get(date)?.find((c) => c.id === id)
    else {
      let scheduledCourse: ScheduledCourse | undefined
      scheduledCourses.value.forEach((scheduledCoursesD) => {
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
    const scheduledCoursesReturn: ScheduledCourse[] = []
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
    let dateString: string = ''
    if (scheduledCourse.start_time) dateString = getDateStringFromTimestamp(scheduledCourse.start_time)
    if (!scheduledCourses.value.has(dateString)) scheduledCourses.value.set(dateString, [])
    const scheduledCoursesOutput = scheduledCourses.value.get(dateString)
    scheduledCoursesOutput!.push(scheduledCourse)
    return scheduledCoursesOutput!
  }

  function addOrUpdateCourseToDate(course: Course): Course[] {
    const dateString = getDateStringFromTimestamp(course.start)
    if (!courses.value.has(dateString)) courses.value.set(dateString, [])
    const coursesOutput = courses.value.get(dateString)
    remove(coursesOutput!, (c) => c.id === course.id)
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
    courseTypeColors,
    courseTypeIds,
    removeCourse,
  }
})
