import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useUndoredo } from '@/composables/undoredo'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { storeToRefs } from 'pinia'
import { setActivePinia, createPinia } from 'pinia'
import { Timestamp } from '@quasar/quasar-ui-qcalendar/dist/types/types'
import { getDateTime, parseTimestamp, parsed, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'
import { useAvailabilityStore } from '@/stores/timetable/availability'

vi.mock('../utils/api.ts')

describe('undoredo composable', () => {
  beforeEach(() => {
    // creates a fresh pinia and make it active so it's automatically picked
    // up by any useStore() call without having to pass it to it:
    // `useStore(pinia)`
    setActivePinia(createPinia())
    const scheduledCourseStore = useScheduledCourseStore()
    const availabilityStore = useAvailabilityStore()
    scheduledCourseStore.addOrUpdateCourseToDate({
      id: 65692,
      no: 1,
      room: 52,
      start: parseTimestamp('2023-04-25 14:15') as Timestamp,
      end: parseTimestamp('2023-04-25 15:20') as Timestamp,
      tutorId: 43,
      suppTutorIds: [55, 3],
      module: 7,
      groupIds: [422, 623, 552],
      courseTypeId: 10,
      roomTypeId: 3,
      graded: false,
      workCopy: 1,
    })
    const { availabilities } = storeToRefs(availabilityStore)
    availabilities.value.set('2022-01-25 14:10', [])
    availabilities.value.get('2022-01-25 14:10')?.push({
      id: 23,
      duration: 120,
      start: parseTimestamp('2022-01-25 14:10') as Timestamp,
      value: 3,
      type: 'user',
      dataId: 4,
    })
  })

  it.skip('historizes an update of a course', () => {
    expect.assertions(2)
    const scheduledCourseStore = useScheduledCourseStore()
    const { addUpdateBlock } = useUndoredo()
    const courseToUpdate = scheduledCourseStore.getCourse(65692, '2023-04-25')
    // addUpdate(
    //   courseToUpdate!.id as number,
    //   {
    //     tutorId: courseToUpdate!.tutorId,
    //     start: parseTimestamp('2022-01-10 08:20') as Timestamp,
    //     end: courseToUpdate!.end,
    //     roomId: courseToUpdate!.room,
    //     suppTutorIds: courseToUpdate!.suppTutorIds,
    //     graded: courseToUpdate!.graded,
    //     roomTypeId: courseToUpdate!.roomTypeId,
    //     groupIds: courseToUpdate!.groupIds,
    //   },
    //   'course'
    // )
    // expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    // addUpdate(
    //   courseToUpdate!.id as number,
    //   {
    //     tutorId: courseToUpdate!.tutorId,
    //     start: updateWorkWeek(parsed('2025-01-10 08:15') as Timestamp),
    //     end: courseToUpdate!.end,
    //     roomId: courseToUpdate!.room,
    //     suppTutorIds: [55, 3],
    //     graded: false,
    //     roomTypeId: 3,
    //     groupIds: [422, 623, 552],
    //   },
    //   'course'
    // )
    // expect(getDateTime(courseToUpdate!.start)).toBe('2025-01-10 08:15')
  })

  it.skip('reverts an update of a course', () => {
    expect.assertions(2)
    const scheduledCourseStore = useScheduledCourseStore()
    const { addUpdateBlock, revertUpdateBlock } = useUndoredo()

    // const courseToUpdate = scheduledCourseStore.getCourse(65692, '2023-04-25')

    // addUpdate(
    //   courseToUpdate!.id as number,
    //   {
    //     tutorId: courseToUpdate!.tutorId,
    //     start: parseTimestamp('2022-01-10 08:20') as Timestamp,
    //     end: courseToUpdate!.end,
    //     roomId: courseToUpdate!.room,
    //     suppTutorIds: courseToUpdate!.suppTutorIds,
    //     graded: courseToUpdate!.graded,
    //     roomTypeId: courseToUpdate!.roomTypeId,
    //     groupIds: courseToUpdate!.groupIds,
    //   },
    //   'course'
    // )

    // expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    // revertUpdate()

    // expect(getDateTime(courseToUpdate!.start)).toBe('2023-04-25 14:15')
  })

  it.todo('reverts several updates of a course', () => {
    expect.assertions(4)
    const scheduledCourseStore = useScheduledCourseStore()
    const { addUpdateBlock, revertUpdateBlock } = useUndoredo()

    // const courseToUpdate = scheduledCourseStore.getCourse(65692, '2023-04-25')
    // addUpdate(
    //   courseToUpdate!.id as number,
    //   {
    //     tutorId: courseToUpdate!.tutorId,
    //     start: updateWorkWeek(parsed('2022-01-10 08:20') as Timestamp),
    //     end: courseToUpdate!.end,
    //     roomId: courseToUpdate?.room || -1,
    //     suppTutorIds: courseToUpdate!.suppTutorIds,
    //     graded: courseToUpdate!.graded,
    //     roomTypeId: courseToUpdate!.roomTypeId,
    //     groupIds: courseToUpdate!.groupIds,
    //   },
    //   'course'
    // )

    // expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    // addUpdate(
    //   courseToUpdate!.id as number,
    //   {
    //     tutorId: courseToUpdate!.tutorId,
    //     start: updateWorkWeek(parsed('2025-01-10 08:15') as Timestamp),
    //     end: courseToUpdate!.end,
    //     roomId: courseToUpdate?.room || -1,
    //     suppTutorIds: [],
    //     graded: false,
    //     roomTypeId: -1,
    //     groupIds: [],
    //   },
    //   'course'
    // )

    // expect(getDateTime(courseToUpdate!.start)).toBe('2025-01-10 08:15')

    // revertUpdate()

    // expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    // revertUpdate()

    // expect(getDateTime(courseToUpdate!.start)).toBe('2023-04-25 14:15')
  })

  it.todo('historizes an update of an availability', () => {
    const availabilityStore = useAvailabilityStore()
    const { addUpdateBlock } = useUndoredo()
    const availToUpdate = availabilityStore.getAvailability(23)
    // addUpdate(
    //   availToUpdate!.id as number,
    //   {
    //     start: parseTimestamp('2022-01-25 14:00') as Timestamp,
    //     value: 1,
    //     duration: 60,
    //   },
    //   'availability'
    // )
    // expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 14:00')
    // expect(availToUpdate!.value).toBe(1)
    // expect(availToUpdate!.duration).toBe(60)

    // addUpdate(
    //   availToUpdate!.id as number,
    //   {
    //     start: parseTimestamp('2023-04-22 16:00') as Timestamp,
    //     value: 7,
    //     duration: 150,
    //   },
    //   'availability'
    // )
    // expect(getDateTime(availToUpdate!.start)).toBe('2023-04-22 16:00')
    // expect(availToUpdate!.value).toBe(7)
    // expect(availToUpdate!.duration).toBe(150)
  })

  it.todo('reverts an update of an availability', () => {
    const availabilityStore = useAvailabilityStore()
    const { addUpdateBlock, revertUpdateBlock } = useUndoredo()
    const availToUpdate = availabilityStore.getAvailability(23)

    // addUpdate(
    //   availToUpdate!.id as number,
    //   {
    //     start: parseTimestamp('2022-01-25 14:00') as Timestamp,
    //     value: 1,
    //     duration: 60,
    //   },
    //   'availability'
    // )
    // expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 14:00')
    // expect(availToUpdate!.value).toBe(1)
    // expect(availToUpdate!.duration).toBe(60)
    // revertUpdate()
    // expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 14:10')
    // expect(availToUpdate!.value).toBe(3)
    // expect(availToUpdate!.duration).toBe(120)
  })

  it.todo('reverts several updates of an availability', () => {})
})
