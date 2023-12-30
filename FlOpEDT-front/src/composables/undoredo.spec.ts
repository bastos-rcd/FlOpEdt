import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useUndoredo } from '@/composables/undoredo'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { storeToRefs } from 'pinia'
import { setActivePinia, createPinia } from 'pinia'
import { Timestamp } from '@quasar/quasar-ui-qcalendar/dist/types/types'
import { getDateTime, parsed, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'

vi.mock('../utils/api.ts')

describe('undoredo composable', () => {
  beforeEach(() => {
    // creates a fresh pinia and make it active so it's automatically picked
    // up by any useStore() call without having to pass it to it:
    // `useStore(pinia)`
    setActivePinia(createPinia())
  })

  it.skip('historize an update of a course', () => {
    expect.assertions(2)
    const scheduledCourseStore = useScheduledCourseStore()
    const { courses } = storeToRefs(scheduledCourseStore)
    const { addUpdate } = useUndoredo()

    const courseToUpdate = courses.value.find((sc) => sc.id === 65692)
    addUpdate(
      courseToUpdate!.id as number,
      {
        tutorId: courseToUpdate!.tutorId,
        start: updateWorkWeek(parsed('2022-01-10 08:20') as Timestamp),
        end: courseToUpdate!.end,
        roomId: courseToUpdate?.room || -1,
        suppTutorIds: courseToUpdate!.suppTutorIds,
        graded: courseToUpdate!.graded,
        roomTypeId: courseToUpdate!.roomTypeId,
        groupIds: courseToUpdate!.groupIds,
      },
      'course'
    )
    expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    addUpdate(
      courseToUpdate!.id as number,
      {
        tutorId: courseToUpdate!.tutorId,
        start: updateWorkWeek(parsed('2025-01-10 08:15') as Timestamp),
        end: courseToUpdate!.end,
        roomId: courseToUpdate?.room || -1,
        suppTutorIds: [],
        graded: false,
        roomTypeId: -1,
        groupIds: [],
      },
      'course'
    )
    expect(getDateTime(courseToUpdate!.start)).toBe('2025-01-10 08:15')
  })

  it.skip('revert an update of a course', () => {
    expect.assertions(2)
    const scheduledCourseStore = useScheduledCourseStore()
    const { courses } = storeToRefs(scheduledCourseStore)
    const { addUpdate, revertUpdate } = useUndoredo()

    const courseToUpdate = courses.value.find((course) => course.id === 65692)
    addUpdate(
      courseToUpdate!.id as number,
      {
        tutorId: courseToUpdate!.tutorId,
        start: updateWorkWeek(parsed('2022-01-10 08:20') as Timestamp),
        end: courseToUpdate!.end,
        roomId: courseToUpdate?.room || -1,
        suppTutorIds: courseToUpdate!.suppTutorIds,
        graded: courseToUpdate!.graded,
        roomTypeId: courseToUpdate!.roomTypeId,
        groupIds: courseToUpdate!.groupIds,
      },
      'course'
    )

    expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    revertUpdate()

    expect(getDateTime(courseToUpdate!.start)).toBe('2023-04-25 14:15')
  })

  it.skip('revert several updates of a course', () => {
    expect.assertions(4)
    const scheduledCourseStore = useScheduledCourseStore()
    const { courses } = storeToRefs(scheduledCourseStore)
    const { addUpdate, revertUpdate } = useUndoredo()

    const courseToUpdate = courses.value.find((course) => course.id === 65692)

    addUpdate(
      courseToUpdate!.id as number,
      {
        tutorId: courseToUpdate!.tutorId,
        start: updateWorkWeek(parsed('2022-01-10 08:20') as Timestamp),
        end: courseToUpdate!.end,
        roomId: courseToUpdate?.room || -1,
        suppTutorIds: courseToUpdate!.suppTutorIds,
        graded: courseToUpdate!.graded,
        roomTypeId: courseToUpdate!.roomTypeId,
        groupIds: courseToUpdate!.groupIds,
      },
      'course'
    )

    expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    addUpdate(
      courseToUpdate!.id as number,
      {
        tutorId: courseToUpdate!.tutorId,
        start: updateWorkWeek(parsed('2025-01-10 08:15') as Timestamp),
        end: courseToUpdate!.end,
        roomId: courseToUpdate?.room || -1,
        suppTutorIds: [],
        graded: false,
        roomTypeId: -1,
        groupIds: [],
      },
      'course'
    )

    expect(getDateTime(courseToUpdate!.start)).toBe('2025-01-10 08:15')

    revertUpdate()

    expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    revertUpdate()

    expect(getDateTime(courseToUpdate!.start)).toBe('2023-04-25 14:15')
  })
})
