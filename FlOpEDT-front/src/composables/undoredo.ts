import { ref } from "vue"
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { storeToRefs } from 'pinia'

export function useUndoredo () {

  const scheduledCourseStore = useScheduledCourseStore()
  const { scheduledCourses } = storeToRefs(scheduledCourseStore)

  const updatesHistory = ref<any[]>([])

  function addUpdate(currentScheduledCourseId: number | null, data: {
    tutor?: string
    date: string
    time: string
  }) {
    if (currentScheduledCourseId === null) return
    const currentScheduledCourse = scheduledCourses.value.find(sc => sc.id === currentScheduledCourseId)
    if (!currentScheduledCourse) return
    updatesHistory.value.push({
      scheduledCourseId: currentScheduledCourse?.id,
      from: {
        tutor: currentScheduledCourse?.tutor,
        start: currentScheduledCourse?.start_time,
      },
      to: {
        tutor: data.tutor || currentScheduledCourse?.tutor,
        start: data.date + 'T' + data.time + ':00'
      }
    })
    // @ts-expect-error
    currentScheduledCourse.start_time = data.date + 'T' + data.time + ':00'
  }
  function revertUpdate() {
    const lastUpdate = updatesHistory.value.pop()
    const lastScheduledCourseUpdated = scheduledCourses.value.find(sc => sc.id === lastUpdate.scheduledCourseId)
    // @ts-expect-error
    lastScheduledCourseUpdated.start_time = lastUpdate.from.start
  }

  return {
    addUpdate,
    revertUpdate
  }
}
