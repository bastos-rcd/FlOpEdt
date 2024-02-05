import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia, storeToRefs } from 'pinia'
import { useScheduledCourseStore } from './course'
import { ScheduledCourse } from '@/ts/type'
import { Course } from '../declarations'
import { Timestamp, parseTimestamp } from '@quasar/quasar-ui-qcalendar'

describe('Availibility store utils', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const courseStore = useScheduledCourseStore()
    courseStore.addOrUpdateCourseToDate({
      id: 144,
      no: 3,
      room: 90,
      start: parseTimestamp('2023-04-24 08:15') as Timestamp,
      end: parseTimestamp('2023-04-24 12:15') as Timestamp,
      tutorId: 18,
      suppTutorIds: [13, 50, 123],
      module: 33,
      groupIds: [3, 4, 9, 10],
      courseTypeId: 3,
      roomTypeId: 8,
      graded: true,
      workCopy: 3,
    })
    courseStore.addScheduledCourseToDate({
      id: 23,
      roomId: 123,
      start_time: new Date('2017-01-15 14:30'),
      end_time: new Date('2017-01-15 15:50'),
      courseId: 33,
      tutor: 12,
      id_visio: -1,
      moduleId: 424,
      trainProgId: 45,
      groupIds: [23, 24],
      suppTutorsIds: [303, 194],
    })
  })

  it('converts a scheduledCourse object into a course object', () => {
    const courseStore = useScheduledCourseStore()
    const scheduledCourse: ScheduledCourse | undefined = courseStore.getScheduldedCourse(23)
    const course: Course = courseStore.scheduledCourseToCourse(scheduledCourse!)
    expect(course.id).toBe(23)
    expect(course.no).toBe(-1) //not implemented
    expect(course.start).toEqual(parseTimestamp('2017-01-15 14:30'))
    expect(course.room).toBe(123)
    expect(course.end).toEqual(parseTimestamp('2017-01-15 15:50'))
    expect(course.tutorId).toBe(12)
    expect(course.suppTutorIds).toEqual([303, 194])
    expect(course.module).toBe(424)
    expect(course.groupIds).toEqual([23, 24])
    expect(course.courseTypeId).toBe(-1) //not implemented
    expect(course.roomTypeId).toBe(-1) //not implemented
    expect(course.graded).toBe(false) //not implemented
    expect(course.workCopy).toBe(0) //not implemented
  })

  it('converts a course object into a scheduledCourse object', () => {
    const courseStore = useScheduledCourseStore()
    const course: Course = courseStore.getCourse(144) as Course
    const scheduledCourse: ScheduledCourse = courseStore.courseToScheduledCourse(course)
    expect(scheduledCourse.id).toBe(144)
    expect(scheduledCourse.roomId).toBe(90)
    expect(scheduledCourse.start_time).toEqual(new Date('2023-04-24 08:15'))
    expect(scheduledCourse.end_time).toEqual(new Date('2023-04-24 12:15'))
    expect(scheduledCourse.courseId).toBe(-1) //not implemented
    expect(scheduledCourse.tutor).toBe(18)
    expect(scheduledCourse.id_visio).toBe(-1) //not implemented
    expect(scheduledCourse.moduleId).toBe(33)
    expect(scheduledCourse.trainProgId).toBe(-1) //not implemented
    expect(scheduledCourse.groupIds).toEqual([3, 4, 9, 10])
    expect(scheduledCourse.suppTutorsIds).toEqual([13, 50, 123])
  })

  it('converts a scheduledCourse object into a course object and back', () => {
    const courseStore = useScheduledCourseStore()
    const scheduledCourse: ScheduledCourse = courseStore.getScheduldedCourse(23) as ScheduledCourse
    const course: Course = courseStore.scheduledCourseToCourse(scheduledCourse)
    expect(course.id).toBe(23)
    expect(course.no).toBe(-1) //not implemented
    expect(course.start).toEqual(parseTimestamp('2017-01-15 14:30'))
    expect(course.room).toBe(123)
    expect(course.end).toEqual(parseTimestamp('2017-01-15 15:50'))
    expect(course.tutorId).toBe(12)
    expect(course.suppTutorIds).toEqual([303, 194])
    expect(course.module).toBe(424)
    expect(course.groupIds).toEqual([23, 24])
    expect(course.courseTypeId).toBe(-1) //not implemented
    expect(course.roomTypeId).toBe(-1) //not implemented
    expect(course.graded).toBe(false) //not implemented
    expect(course.workCopy).toBe(0) //not implemented

    const newScheduledCourse: ScheduledCourse = courseStore.courseToScheduledCourse(course)
    expect(newScheduledCourse.id).toBe(23)
    expect(newScheduledCourse.roomId).toBe(123)
    expect(newScheduledCourse.start_time).toEqual(new Date('2017-01-15 14:30'))
    expect(newScheduledCourse.end_time).toEqual(new Date('2017-01-15 15:50'))
    expect(newScheduledCourse.courseId).toBe(33) //not implemented
    expect(newScheduledCourse.tutor).toBe(12)
    expect(newScheduledCourse.id_visio).toBe(-1) //not implemented
    expect(newScheduledCourse.moduleId).toBe(424)
    expect(newScheduledCourse.trainProgId).toBe(45) //not implemented
    expect(newScheduledCourse.groupIds).toEqual([23, 24])
    expect(newScheduledCourse.suppTutorsIds).toEqual([303, 194])
  })

  it('converts a course object into a scheduledCourse object and back', () => {
    const courseStore = useScheduledCourseStore()
    const course: Course = courseStore.getCourse(144) as Course
    const scheduledCourse: ScheduledCourse = courseStore.courseToScheduledCourse(course)
    expect(scheduledCourse.id).toBe(144)
    expect(scheduledCourse.roomId).toBe(90)
    expect(scheduledCourse.start_time).toEqual(new Date('2023-04-24 08:15'))
    expect(scheduledCourse.end_time).toEqual(new Date('2023-04-24 12:15'))
    expect(scheduledCourse.courseId).toBe(-1) //not implemented
    expect(scheduledCourse.tutor).toBe(18)
    expect(scheduledCourse.id_visio).toBe(-1) //not implemented
    expect(scheduledCourse.moduleId).toBe(33)
    expect(scheduledCourse.trainProgId).toBe(-1) //not implemented
    expect(scheduledCourse.groupIds).toEqual([3, 4, 9, 10])
    expect(scheduledCourse.suppTutorsIds).toEqual([13, 50, 123])
    const newCourse: Course = courseStore.scheduledCourseToCourse(scheduledCourse)
    expect(newCourse.id).toBe(144)
    expect(newCourse.no).toBe(-1) //not implemented
    expect(newCourse.start).toEqual(parseTimestamp('2023-04-24 08:15'))
    expect(newCourse.room).toBe(90)
    expect(newCourse.end).toEqual(parseTimestamp('2023-04-24 12:15'))
    expect(newCourse.tutorId).toBe(18)
    expect(newCourse.suppTutorIds).toEqual([13, 50, 123])
    expect(newCourse.module).toBe(33)
    expect(newCourse.groupIds).toEqual([3, 4, 9, 10])
    expect(newCourse.courseTypeId).toBe(-1) //not implemented
    expect(newCourse.roomTypeId).toBe(-1) //not implemented
    expect(newCourse.graded).toBe(false) //not implemented
    expect(newCourse.workCopy).toBe(0) //not implemented
  })

  it("gets an item from the store if it's presents or returns undefined value", () => {
    const courseStore = useScheduledCourseStore()
    const course = courseStore.getCourse(144)
    const scheduledCourse = courseStore.getScheduldedCourse(23)
    const notExistentCourse = courseStore.getCourse(1)
    const notExistentScheduledCourse = courseStore.getScheduldedCourse(1)
    expect(course).toBeDefined()
    expect(scheduledCourse).toBeDefined()
    expect(notExistentCourse).toBeUndefined()
    expect(notExistentScheduledCourse).toBeUndefined()
  })

  it('adds scheduledCourses happening the same day to the same key', () => {
    const courseStore = useScheduledCourseStore()
    expect(courseStore.getScheduledCoursesFromDateToDate(parseTimestamp('2017-01-15')!).length).toBe(1)
    expect(courseStore.getScheduledCoursesFromDateToDate(parseTimestamp('2018-01-16')!).length).toBe(0)
    let scheduledCoursesOnDate = courseStore.addScheduledCourseToDate({
      id: 23,
      roomId: 123,
      start_time: new Date('2018-01-16 14:30'),
      end_time: new Date('2018-01-16 15:50'),
      courseId: 33,
      tutor: 12,
      id_visio: -1,
      moduleId: 424,
      trainProgId: 45,
      groupIds: [23, 24],
      suppTutorsIds: [303, 194],
    })
    expect(courseStore.getScheduledCoursesFromDateToDate(parseTimestamp('2017-01-15')!).length).toBe(1)
    expect(courseStore.getScheduledCoursesFromDateToDate(parseTimestamp('2018-01-16')!).length).toBe(1)
    expect(courseStore.getScheduledCoursesFromDateToDate(parseTimestamp('2018-01-16')!)).toEqual(scheduledCoursesOnDate)
    scheduledCoursesOnDate = courseStore.addScheduledCourseToDate({
      id: 246,
      roomId: 13,
      start_time: new Date('2018-01-16 09:30'),
      end_time: new Date('2018-01-16 11:50'),
      courseId: 3,
      tutor: 1,
      id_visio: -1,
      moduleId: 4,
      trainProgId: 45,
      groupIds: [24],
      suppTutorsIds: [],
    })
    expect(courseStore.getScheduledCoursesFromDateToDate(parseTimestamp('2017-01-15')!).length).toBe(1)
    expect(courseStore.getScheduledCoursesFromDateToDate(parseTimestamp('2018-01-16')!).length).toBe(2)
    expect(courseStore.getScheduledCoursesFromDateToDate(parseTimestamp('2018-01-16')!)).toEqual(scheduledCoursesOnDate)
  })
})
