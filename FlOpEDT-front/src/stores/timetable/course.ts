import { api } from '@/utils/api'
import { defineStore, storeToRefs } from 'pinia'
import { computed, ref } from 'vue'
import { ScheduledCourse, Department } from '@/ts/type'
import { Course, Module } from '@/stores/declarations'
import { Timestamp, copyTimestamp, makeDate, nextDay, parseTime, updateFormatted } from '@quasar/quasar-ui-qcalendar'
import _, { cloneDeep } from 'lodash'
import { dateToTimestamp, getDateStringFromTimestamp, getDateTimeStringFromDate, timestampToDate } from '@/helpers'
import { InputCalendarEvent } from '@/components/calendar/declaration'
import { usePermanentStore } from './permanent'
import { useGroupStore } from './group'

/**
 * This store is a work in progress,
 * related to the ScheduleView for beginning.
 *
 * This store is not related to the scheduledCourse
 */
export const useScheduledCourseStore = defineStore('scheduledCourse', () => {
  const permanentStore = usePermanentStore()
  const groupStore = useGroupStore()
  const { modules, moduleColor } = storeToRefs(permanentStore)

  const scheduledCourses = ref<Map<string, ScheduledCourse[]>>(new Map<string, ScheduledCourse[]>())
  const courses = ref<Map<string, Course[]>>(new Map<string, Course[]>())
  const courseCalendarEvents = computed((): Map<string, InputCalendarEvent[]> => {
    const calendarEvents: Map<string, InputCalendarEvent[]> = new Map<string, InputCalendarEvent[]>()
    courses.value.forEach((coursesOnDate, date) => {
      if (!calendarEvents.has(date)) calendarEvents.set(date, [])
      coursesOnDate.forEach((c) => {
        const module: Module | undefined = modules.value.find((m) => m.id === c.module)
        const currentEvent: InputCalendarEvent = {
          id: -1,
          title: module ? module.abbrev : 'Cours',
          toggled: true,
          bgcolor: 'blue',
          columnIds: [],
          data: {
            dataId: c.id,
            dataType: 'event',
            start: copyTimestamp(c.start),
            duration: parseTime(c.end) - parseTime(c.start),
          },
        }
        if (module) {
          currentEvent.bgcolor = moduleColor.value.get(module.id)!
        }
        c.groupIds.forEach((courseGroup) => {
          const currentGroup = groupStore.groups.find((g) => g.id === courseGroup)
          if (currentGroup) {
            currentGroup.columnIds.forEach((cI) => {
              currentEvent.columnIds.push(cI)
            })
          }
        })
        calendarEvents.get(date)?.push(currentEvent)
      })
    })
    return calendarEvents
  })
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
      suppTutorIds: cloneDeep(scheduledCourse.suppTutorsIds),
      module: scheduledCourse.moduleId,
      groupIds: cloneDeep(scheduledCourse.groupIds),
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
      scheduledCourse.suppTutorsIds = cloneDeep(course.suppTutorIds)
      scheduledCourse.groupIds = cloneDeep(course.groupIds)
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
        groupIds: cloneDeep(course.groupIds),
        suppTutorsIds: cloneDeep(course.suppTutorIds),
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

  function getCalendarCourseEvent(id: number, date?: string): InputCalendarEvent | undefined {
    if (date) return courseCalendarEvents.value.get(date)?.find((c) => c.id === id)
    else {
      let calendarCourseEvent: InputCalendarEvent | undefined
      courseCalendarEvents.value.forEach((courseCalendarEventsD, date) => {
        calendarCourseEvent = courseCalendarEventsD.find((c) => c.id === id)
        if (calendarCourseEvent) return
      })
      return calendarCourseEvent
    }
  }

  function getCoursesFromDateToDate(from: Timestamp, to?: Timestamp): Course[] {
    let coursesReturn: Course[] = []
    if (!to)
      courses.value.get(getDateStringFromTimestamp(from))?.forEach((c) => {
        coursesReturn.push(c)
      })
    else {
      let currentDate = copyTimestamp(from)
      while (currentDate.weekday !== to.weekday) {
        courses.value.get(getDateStringFromTimestamp(currentDate))?.forEach((c) => {
          coursesReturn.push(c)
        })
        currentDate = updateFormatted(nextDay(currentDate))
      }
    }
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

  function getCalendarCoursesFromDateToDate(from: Timestamp, to?: Timestamp): InputCalendarEvent[] {
    let courseCalendarEventsReturn: InputCalendarEvent[] = []
    if (!to) {
      courseCalendarEvents.value.get(getDateStringFromTimestamp(from))?.forEach((c) => {
        courseCalendarEventsReturn.push(c)
      })
    } else {
      let currentDate = copyTimestamp(from)
      while (currentDate.weekday !== to.weekday) {
        courseCalendarEvents.value.get(getDateStringFromTimestamp(currentDate))?.forEach((c) => {
          courseCalendarEventsReturn.push(c)
        })
        currentDate = updateFormatted(nextDay(currentDate))
      }
    }
    return courseCalendarEventsReturn
  }

  // function addCalendarCourseToDate(calendarCourse: InputCalendarEvent): InputCalendarEvent[] {
  //   const dateString = getDateStringFromTimestamp(calendarCourse.data.start)
  //   if (!courses.value.has(dateString)) courses.value.set(dateString, [])
  //   // if (!courseCalendarEvents.value.has(dateString)) courseCalendarEvents.value.set(dateString, [])
  //   // const courseCalendarEventsOutput = courseCalendarEvents.value.get(dateString)
  //   // courseCalendarEventsOutput!.push(calendarCourse)
  //   // return courseCalendarEventsOutput!
  // }

  function addScheduledCourseToDate(scheduledCourse: ScheduledCourse): ScheduledCourse[] {
    const dateString = getDateTimeStringFromDate(scheduledCourse.start_time, false)
    if (!scheduledCourses.value.has(dateString)) scheduledCourses.value.set(dateString, [])
    const scheduledCoursesOutput = scheduledCourses.value.get(dateString)
    scheduledCoursesOutput!.push(scheduledCourse)
    return scheduledCoursesOutput!
  }

  function addCourseToDate(course: Course): Course[] {
    const dateString = getDateStringFromTimestamp(course.start)
    if (!courses.value.has(dateString)) courses.value.set(dateString, [])
    const coursesOutput = courses.value.get(dateString)
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
    getCalendarCourseEvent,
    getCoursesFromDateToDate,
    getScheduledCoursesFromDateToDate,
    getCalendarCoursesFromDateToDate,
    // addCalendarCourseToDate,
    addScheduledCourseToDate,
    addCourseToDate,
    courseCalendarEvents,
  }
})
