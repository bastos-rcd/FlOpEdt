import { ref } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { storeToRefs } from 'pinia'
import { AvailabilityData, CourseData, UpdateCourse, UpdatesHistory } from './declaration'

export function useUndoredo() {
  const scheduledCourseStore = useScheduledCourseStore()
  const { courses } = storeToRefs(scheduledCourseStore)

  const updatesHistory = ref<UpdatesHistory[]>([])

  function addUpdate(objectId: number | null, data: CourseData | AvailabilityData, type: 'course' | 'availability') {
    if (objectId === null) return
    if (type === 'course') {
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
        to: data,
      } as UpdateCourse)
    } else if (type === 'availability') {
      // TODO
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
    }
  }

  return {
    addUpdate,
    revertUpdate,
  }
}
