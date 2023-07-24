import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useUndoredo } from '@/composables/undoredo'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { storeToRefs } from 'pinia'
import { getScheduledCoursesData } from '@/composables/scheduled'
import { ScheduledCourse } from '@/ts/type'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('../utils/api.ts')

describe('undoredo composable', () => {
  beforeEach(() => {
    // creates a fresh pinia and make it active so it's automatically picked
    // up by any useStore() call without having to pass it to it:
    // `useStore(pinia)`
    setActivePinia(createPinia())
  })
  it.todo('historize an update of a scheduled course')
  /*
  it('historize an update of a scheduled course', () => {
    expect.assertions(2)
    const scheduledCourseStore = useScheduledCourseStore()
    const { scheduledCourses } = storeToRefs(scheduledCourseStore)
    const { addUpdate } = useUndoredo()

    scheduledCourses.value = getScheduledCoursesData() as unknown as ScheduledCourse[]

    const scheduledCourseToUpdate = scheduledCourses.value.find((sc) => sc.id === 65692)

    addUpdate(scheduledCourseToUpdate!.id as number, {
      date: '2022-01-10',
      time: '08:20',
    })

    expect(scheduledCourseToUpdate?.start_time).toBe('2022-01-10T08:20:00')

    addUpdate(scheduledCourseToUpdate!.id as number, {
      date: '2025-01-10',
      time: '08:15',
    })

    expect(scheduledCourseToUpdate?.start_time).toBe('2025-01-10T08:15:00')
  })

  it('revert an update of a scheduled course', () => {
    expect.assertions(2)
    const scheduledCourseStore = useScheduledCourseStore()
    const { scheduledCourses } = storeToRefs(scheduledCourseStore)
    const { addUpdate, revertUpdate } = useUndoredo()

    scheduledCourses.value = getScheduledCoursesData() as unknown as ScheduledCourse[]

    const scheduledCourseToUpdate = scheduledCourses.value.find((sc) => sc.id === 65692)
    addUpdate(scheduledCourseToUpdate!.id as number, {
      date: '2022-01-10',
      time: '08:20',
    })

    expect(scheduledCourseToUpdate?.start_time).toBe('2022-01-10T08:20:00')

    revertUpdate()

    expect(scheduledCourseToUpdate?.start_time).toBe('2023-04-25T14:15:00')
  })

  it('revert several updates of a scheduled course', () => {
    expect.assertions(4)
    const scheduledCourseStore = useScheduledCourseStore()
    const { scheduledCourses } = storeToRefs(scheduledCourseStore)
    const { addUpdate, revertUpdate } = useUndoredo()

    scheduledCourses.value = getScheduledCoursesData() as unknown as ScheduledCourse[]

    const scheduledCourseToUpdate = scheduledCourses.value.find((sc) => sc.id === 65692)

    addUpdate(scheduledCourseToUpdate!.id as number, {
      date: '2022-01-10',
      time: '08:20',
    })

    expect(scheduledCourseToUpdate?.start_time).toBe('2022-01-10T08:20:00')

    addUpdate(scheduledCourseToUpdate!.id as number, {
      date: '2025-01-10',
      time: '08:15',
    })

    expect(scheduledCourseToUpdate?.start_time).toBe('2025-01-10T08:15:00')

    revertUpdate()

    expect(scheduledCourseToUpdate?.start_time).toBe('2022-01-10T08:20:00')

    revertUpdate()

    expect(scheduledCourseToUpdate?.start_time).toBe('2023-04-25T14:15:00')
  })
  */
})
