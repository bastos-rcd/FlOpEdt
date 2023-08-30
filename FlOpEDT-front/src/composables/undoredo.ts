import { ref } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { storeToRefs } from 'pinia'
import { AvailabilityData, CourseData, UpdateAvailability, UpdateCourse, UpdatesHistory } from './declaration'
import { Timestamp, parsed, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'

export function useUndoredo() {
  const scheduledCourseStore = useScheduledCourseStore()
  const { courses } = storeToRefs(scheduledCourseStore)

  const updatesHistory = ref<UpdatesHistory[]>([])

  function addUpdate(objectId: number | null, data: CourseData | AvailabilityData, type: 'course' | 'availability') {
    if (objectId === null) return
    if (type === 'course') {
      const courseData = data as CourseData
      const currentCourse = courses.value.find((course) => course.id === objectId)
      if (!currentCourse) return
      updatesHistory.value.push({
        type: type,
        objectId: currentCourse?.id,
        from: {
          tutorId: currentCourse?.tutorId,
          start: currentCourse.start,
          end: currentCourse.end,
          roomId: currentCourse.room,
          suppTutorIds: currentCourse.suppTutorIds,
          graded: currentCourse.graded,
          roomTypeId: currentCourse.roomTypeId,
          groupIds: currentCourse.groupIds,
        },
        to: courseData,
      } as UpdateCourse)
      currentCourse.tutorId = courseData.tutorId
      currentCourse.start = courseData.start
      currentCourse.end = courseData.end
      currentCourse.room = courseData.roomId
      currentCourse.suppTutorIds = courseData.suppTutorIds
      currentCourse.graded = courseData.graded
      currentCourse.roomTypeId = courseData.roomTypeId
      currentCourse.groupIds = courseData.groupIds
    } else if (type === 'availability') {
      const availData = data as AvailabilityData
      // TODO call to API/store to retrieve the avail
      const currentAvail = {
        id: 1,
        start: updateWorkWeek(parsed('2022-01-10 08:20') as Timestamp),
        end: updateWorkWeek(parsed('2022-01-10 11:20') as Timestamp),
        duration: 180,
        value: 5,
      }
      if (!currentAvail) return
      updatesHistory.value.push({
        type: type,
        objectId: currentAvail?.id,
        from: {
          start: currentAvail.start,
          end: currentAvail.end,
          value: currentAvail.value,
          duration: currentAvail.duration,
        },
        to: availData,
      } as UpdateAvailability)
      currentAvail.duration = availData.duration
      currentAvail.value = availData.value
      currentAvail.start = availData.start
      currentAvail.end = availData.end
    }
  }

  function revertUpdate() {
    const lastUpdate: UpdatesHistory | undefined = updatesHistory.value.pop()
    if (lastUpdate === undefined) return
    if (lastUpdate?.type === 'course') {
      const lastCourseUpdate = lastUpdate as UpdateCourse
      const lastScheduledCourseUpdated = courses.value.find((course) => course.id === lastCourseUpdate?.objectId)
      lastScheduledCourseUpdated!.tutorId = lastCourseUpdate.from.tutorId
      lastScheduledCourseUpdated!.start = lastCourseUpdate.from.start
      lastScheduledCourseUpdated!.end = lastCourseUpdate.from.end
      lastScheduledCourseUpdated!.room = lastCourseUpdate.from.roomId
      lastScheduledCourseUpdated!.suppTutorIds = lastCourseUpdate.from.suppTutorIds
      lastScheduledCourseUpdated!.graded = lastCourseUpdate.from.graded
      lastScheduledCourseUpdated!.roomTypeId = lastCourseUpdate.from.roomTypeId
      lastScheduledCourseUpdated!.groupIds = lastCourseUpdate.from.groupIds
    } else if (lastUpdate?.type === 'availability') {
      // TODO call to API/store to retrieve the avail
      const lastAvailUpdate = lastUpdate as UpdateAvailability
      const lastAvailUpdated = {
        id: 1,
        start: updateWorkWeek(parsed('2022-01-10 08:20') as Timestamp),
        end: updateWorkWeek(parsed('2022-01-10 11:20') as Timestamp),
        duration: 180,
        value: 5,
      }
      lastAvailUpdated.duration = lastAvailUpdate.from.duration
      lastAvailUpdated.start = lastAvailUpdate.from.start
      lastAvailUpdated.end = lastAvailUpdate.from.end
      lastAvailUpdated.value = lastAvailUpdate.from.value
    }
  }
  return {
    addUpdate,
    revertUpdate,
  }
}
