import { computed, ref } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { AvailabilityData, CourseData, UpdateAvailability, UpdateCourse, UpdatesHistory } from './declaration'
import { useAvailabilityStore } from '@/stores/timetable/availability'
import { Availability } from '@/stores/declarations'
import { cloneDeep } from 'lodash'
import { getDate } from '@quasar/quasar-ui-qcalendar'

export function useUndoredo() {
  const scheduledCourseStore = useScheduledCourseStore()
  const availabilityStore = useAvailabilityStore()
  const hasUpdate = computed(() => {
    return updatesHistories.value.length !== 0
  })
  const updatesHistories = ref<UpdatesHistory[][]>([])

  function addUpdate(
    objectId: number | null,
    data: CourseData | AvailabilityData,
    type: 'course' | 'availability',
    operation: 'update' | 'create' | 'remove' = 'update'
  ): UpdatesHistory | undefined {
    if (objectId === null) return
    if (type === 'course') {
      const courseData = data as CourseData
      const currentCourse = scheduledCourseStore.getCourse(objectId, undefined, true)
      if (operation === 'update') {
        if (!currentCourse) return
        const courseDataFrom = {
          tutorId: currentCourse.tutorId,
          start: currentCourse.start,
          end: currentCourse.end,
          roomId: currentCourse.room,
          suppTutorIds: currentCourse.suppTutorIds,
          graded: currentCourse.graded,
          roomTypeId: currentCourse.roomTypeId,
          groupIds: currentCourse.groupIds,
        }
        currentCourse.tutorId = courseData.tutorId
        currentCourse.start = courseData.start
        currentCourse.end = courseData.end
        currentCourse.room = courseData.roomId
        currentCourse.suppTutorIds = courseData.suppTutorIds
        currentCourse.graded = courseData.graded
        currentCourse.roomTypeId = courseData.roomTypeId
        currentCourse.groupIds = courseData.groupIds
        scheduledCourseStore.addOrUpdateCourseToDate(currentCourse)
        return {
          type: type,
          objectId: currentCourse.id,
          from: courseDataFrom,
          to: courseData,
          operation: operation,
        } as UpdateCourse
      } else if (operation === 'remove') {
        if (!currentCourse) return
        const dataFrom = {
          tutorId: currentCourse.tutorId,
          start: currentCourse.start,
          end: currentCourse.end,
          roomId: currentCourse.room,
          suppTutorIds: currentCourse.suppTutorIds,
          graded: currentCourse.graded,
          roomTypeId: currentCourse.roomTypeId,
          groupIds: currentCourse.groupIds,
        }
        scheduledCourseStore.removeCourse(currentCourse.id, getDate(currentCourse.start))
        return {
          objectId: objectId,
          operation: operation,
          type: type,
          to: courseData,
          from: dataFrom,
        } as UpdatesHistory
      } else if (operation === 'create') {
        console.log('TODO')
      }
    } else if (type === 'availability') {
      const availData = data as AvailabilityData
      const dataFrom = cloneDeep(data) as AvailabilityData
      let currentAvail: Availability | undefined
      if (operation === 'update') {
        currentAvail = availabilityStore.getAvailability(objectId)
        if (currentAvail) {
          dataFrom.start = currentAvail.start
          dataFrom.duration = currentAvail.duration
          dataFrom.value = currentAvail.value
        }
      } else if (operation === 'create') {
        const oldAvail = availabilityStore.getAvailability(objectId)
        if (oldAvail) currentAvail = availabilityStore.createNewAvailability(oldAvail)
        dataFrom.value = -1
      } else if (operation === 'remove') {
        currentAvail = availabilityStore.getAvailability(objectId)
        if (currentAvail) {
          dataFrom.start = currentAvail.start
          dataFrom.duration = currentAvail.duration
          dataFrom.value = currentAvail.value
          dataFrom.availType = currentAvail.type
          dataFrom.dataId = currentAvail.dataId
        }
        availabilityStore.removeAvailibility(objectId)
        return {
          type: type,
          objectId: currentAvail?.id || -1,
          from: dataFrom,
          to: availData,
          operation: operation,
        } as UpdateAvailability
      }
      if (currentAvail) {
        currentAvail.duration = availData.duration
        currentAvail.value = availData.value
        currentAvail.start = availData.start
        availabilityStore.addOrUpdateAvailibility(currentAvail)
        return {
          type: type,
          objectId: currentAvail.id,
          from: dataFrom,
          to: availData,
          operation: operation,
        } as UpdateAvailability
      }
    }
  }

  function revertUpdate(update: UpdatesHistory) {
    if (update.type === 'course') {
      const lastCourseUpdate = update as UpdateCourse
      const lastScheduledCourseUpdated = scheduledCourseStore.getCourse(lastCourseUpdate.objectId, undefined, true)
      lastScheduledCourseUpdated!.start = lastCourseUpdate.from.start
      lastScheduledCourseUpdated!.end = lastCourseUpdate.from.end
      lastScheduledCourseUpdated!.room = lastCourseUpdate.from.roomId
      lastScheduledCourseUpdated!.suppTutorIds = lastCourseUpdate.from.suppTutorIds
      lastScheduledCourseUpdated!.graded = lastCourseUpdate.from.graded
      lastScheduledCourseUpdated!.roomTypeId = lastCourseUpdate.from.roomTypeId
      lastScheduledCourseUpdated!.groupIds = lastCourseUpdate.from.groupIds
      scheduledCourseStore.addOrUpdateCourseToDate(lastScheduledCourseUpdated!)
    } else if (update?.type === 'availability') {
      const lastAvailUpdate = update as UpdateAvailability
      if (lastAvailUpdate.operation === 'create') {
        availabilityStore.removeAvailibility(lastAvailUpdate.objectId)
      } else if (lastAvailUpdate.operation === 'update') {
        const lastAvailUpdated = availabilityStore.getAvailability(lastAvailUpdate.objectId)
        lastAvailUpdated!.duration = lastAvailUpdate.from.duration
        lastAvailUpdated!.start = lastAvailUpdate.from.start
        lastAvailUpdated!.value = lastAvailUpdate.from.value
      } else if (lastAvailUpdate.operation === 'remove') {
        const newAvail: Availability = {
          id: -1,
          duration: lastAvailUpdate.from.duration,
          start: lastAvailUpdate.from.start,
          value: lastAvailUpdate.from.value,
          type: lastAvailUpdate.from.availType!,
          dataId: lastAvailUpdate.from.dataId!,
        }
        availabilityStore.addOrUpdateAvailibility(
          availabilityStore.createNewAvailability(newAvail, lastAvailUpdate.objectId)
        )
      }
    }
  }

  function addUpdateBlock(
    updateBlock: {
      data: CourseData | AvailabilityData
      objectId: number
      type: 'course' | 'availability'
      operation: 'update' | 'create' | 'remove'
    }[]
  ): void {
    const updates: UpdatesHistory[] = []
    updateBlock.forEach((update) => {
      const currentUpdate: UpdatesHistory | undefined = addUpdate(
        update.objectId,
        update.data,
        update.type,
        update.operation
      )
      if (currentUpdate) updates.push(currentUpdate)
    })
    updatesHistories.value.push(updates)
  }

  function revertUpdateBlock(): void {
    const updateBlock = updatesHistories.value.pop()
    if (updateBlock) {
      let update = updateBlock.pop()
      while (update) {
        revertUpdate(update)
        update = updateBlock.pop()
      }
    }
  }

  return {
    revertUpdateBlock,
    hasUpdate,
    addUpdateBlock,
    updatesHistories,
  }
}
