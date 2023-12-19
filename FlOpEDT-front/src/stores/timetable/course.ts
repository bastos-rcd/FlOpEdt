import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ScheduledCourse, FlopWeek, Department, Course } from '@/ts/type'
import { Course as CourseFront } from '@/stores/declarations'
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
  const courses = ref<CourseFront[]>([])
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchScheduledCourses(week: FlopWeek, department?: Department): Promise<void> {
    isLoading.value = true
    try {
      await api.getScheduledCourses(week.week, week.year, department?.abbrev).then((result) => {
        result.forEach((r: any) => {
          scheduledCourses.value.push({
            id: r.id,
            roomId: r.room_id,
            start_time: new Date(r.start_time),
            end_time: new Date(r.end_time),
            courseId: r.course_id,
            tutor: r.tutor_id,
            id_visio: -1,
            moduleId: r.module_id,
            trainProgId: r.train_prog_id,
            groupIds: r.group_ids,
            suppTutorsIds: r.supp_tutor_ids,
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
      // graded: TODO
      // roomTypeId: TODO
      scheduledCourse.roomId = course.room
      scheduledCourse.start_time = makeDate(course.start)
      scheduledCourse.end_time = makeDate(course.end)
      scheduledCourse.tutor = course.tutorId
      scheduledCourse.suppTutorsIds = course.suppTutorIds
      scheduledCourse.groupIds = course.groupIds
      // scheduledCourse.module TODO
      // scheduledCourse.courseTypeId TODO
      // scheduledCourse.roomTypeId TODO
      // scheduledCourse.workCopy TODO ?
      _.remove(scheduledCourses.value, (sc) => sc.id === course.id)
      scheduledCourses.value.push(scheduledCourse)
    }
    // TODO UPDATE BACK
  }

  function scheduledCourseToCourse(scheduledCourse: ScheduledCourse): CourseFront {
    let course: CourseFront = {
      id: scheduledCourse.id,
      no: -1,
      room: scheduledCourse.roomId as number,
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
      suppTutorIds: scheduledCourse.suppTutorsIds,
      module: scheduledCourse.moduleId,
      groupIds: scheduledCourse.groupIds,
      courseTypeId: -1,
      roomTypeId: -1,
      graded: false,
      workCopy: 0,
    }
    return course
  }

  function courseToScheduledCourse(course: CourseFront): ScheduledCourse | undefined {
    let scheduledCourse: ScheduledCourse | undefined = scheduledCourses.value.find((sc) => sc.id === course.id)
    if (scheduledCourse) {
      scheduledCourse.roomId = course.room
      scheduledCourse.suppTutorsIds = course.suppTutorIds
      scheduledCourse.moduleId = course.module
      scheduledCourse.groupIds = course.groupIds
      scheduledCourse.start_time = makeDate(course.start)
      scheduledCourse.end_time = makeDate(course.end)
      scheduledCourse.tutor = course.tutorId
      // scheduledCourse.suppTutorIds TODO
      // scheduledCourse.module TODO
      // scheduledCourse.groupIds TODO with groupstore or APIcall
      // scheduledCourse.courseTypeId TODO
      // scheduledCourse.roomTypeId TODO
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
