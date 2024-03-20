import { computed, ref } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { AvailabilityData, CourseData, UpdateAvailability, UpdateCourse, UpdatesHistory } from './declaration'
import { useAvailabilityStore } from '@/stores/timetable/availability'
import { useEventStore } from '@/stores/display/event'
import { Availability } from '@/stores/declarations'

export function useUndoredo() {
  const scheduledCourseStore = useScheduledCourseStore()
  const availabilityStore = useAvailabilityStore()
  const hasUpdate = computed(() => {
    return updatesHistory.value.length !== 0
  })
  const updatesHistory = ref<UpdatesHistory[]>([])

  function addUpdate(
    objectId: number | null,
    data: CourseData | AvailabilityData,
    type: 'course' | 'availability',
    operation: 'update' | 'create' | 'remove' = 'update'
  ) {
    if (objectId === null) return
    if (type === 'course') {
      const courseData = data as CourseData
      const currentCourse = scheduledCourseStore.getCourse(objectId, undefined, true)
      if (!currentCourse) return
      updatesHistory.value.push({
        type: type,
        objectId: currentCourse.id,
        from: {
          tutorId: currentCourse.tutorId,
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
      scheduledCourseStore.addOrUpdateCourseToDate(currentCourse)
    } else if (type === 'availability') {
      const eventStore = useEventStore()
      const availData = data as AvailabilityData
      let currentAvail: Availability | undefined
      if (operation === 'update') currentAvail = availabilityStore.getAvailability(objectId)
      else if (operation === 'create') {
        const availabilityEventRelated = eventStore.calendarEvents.find(
          (ev) => ev.data.dataId === objectId && ev.data.dataType === 'avail'
        )
        if (availabilityEventRelated) currentAvail = availabilityStore.createAvailability(availabilityEventRelated)
      }
      if (currentAvail) {
        updatesHistory.value.push({
          type: type,
          objectId: currentAvail.id,
          from: {
            start: currentAvail.start,
            value: currentAvail.value,
            duration: currentAvail.duration,
          },
          to: availData,
        } as UpdateAvailability)
        currentAvail.duration = availData.duration
        currentAvail.value = availData.value
        currentAvail.start = availData.start
        availabilityStore.addOrUpdateAvailibility(currentAvail)
      }
    }
  }

  function revertUpdate() {
    const lastUpdate: UpdatesHistory | undefined = updatesHistory.value.pop()
    if (lastUpdate !== undefined) {
      if (lastUpdate.type === 'course') {
        const lastCourseUpdate = lastUpdate as UpdateCourse
        const lastScheduledCourseUpdated = scheduledCourseStore.getCourse(lastCourseUpdate.objectId, undefined, true)
        lastScheduledCourseUpdated!.start = lastCourseUpdate.from.start
        lastScheduledCourseUpdated!.end = lastCourseUpdate.from.end
        lastScheduledCourseUpdated!.room = lastCourseUpdate.from.roomId
        lastScheduledCourseUpdated!.suppTutorIds = lastCourseUpdate.from.suppTutorIds
        lastScheduledCourseUpdated!.graded = lastCourseUpdate.from.graded
        lastScheduledCourseUpdated!.roomTypeId = lastCourseUpdate.from.roomTypeId
        lastScheduledCourseUpdated!.groupIds = lastCourseUpdate.from.groupIds
        scheduledCourseStore.addOrUpdateCourseToDate(lastScheduledCourseUpdated!)
      } else if (lastUpdate?.type === 'availability') {
        const lastAvailUpdate = lastUpdate as UpdateAvailability
        const lastAvailUpdated = availabilityStore.getAvailability(lastAvailUpdate.objectId)
        lastAvailUpdated!.duration = lastAvailUpdate.from.duration
        lastAvailUpdated!.start = lastAvailUpdate.from.start
        lastAvailUpdated!.value = lastAvailUpdate.from.value
      }
    }
  }

  return {
    addUpdate,
    revertUpdate,
    hasUpdate,
  }
}
