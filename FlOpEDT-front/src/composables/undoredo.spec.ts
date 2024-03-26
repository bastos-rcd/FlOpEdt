import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useUndoredo } from '@/composables/undoredo'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { storeToRefs } from 'pinia'
import { setActivePinia, createPinia } from 'pinia'
import { Timestamp } from '@quasar/quasar-ui-qcalendar/dist/types/types'
import { getDateTime, parseTimestamp, parsed, today, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'
import { useAvailabilityStore } from '@/stores/timetable/availability'
import { AvailabilityData, CourseData } from './declaration'

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
    availabilities.value.set('2022-01-25', [])
    availabilities.value.get('2022-01-25')?.push({
      id: 23,
      duration: 120,
      start: parseTimestamp('2022-01-25 14:10') as Timestamp,
      value: 3,
      type: 'user',
      dataId: 4,
    })
  })

  it('historizes an update of a course', () => {
    expect.assertions(3)
    const scheduledCourseStore = useScheduledCourseStore()
    const { addUpdateBlock, hasUpdate } = useUndoredo()
    const courseToUpdate = scheduledCourseStore.getCourse(65692, '2023-04-25')
    addUpdateBlock([
      {
        data: {
          tutorId: courseToUpdate!.tutorId,
          start: parseTimestamp('2022-01-10 08:20') as Timestamp,
          end: courseToUpdate!.end,
          roomId: courseToUpdate!.room,
          suppTutorIds: courseToUpdate!.suppTutorIds,
          graded: courseToUpdate!.graded,
          roomTypeId: courseToUpdate!.roomTypeId,
          groupIds: courseToUpdate!.groupIds,
        },
        objectId: courseToUpdate!.id,
        type: 'course',
        operation: 'update',
      },
    ])
    expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')
    expect(hasUpdate.value).toBe(true)

    addUpdateBlock([
      {
        data: {
          tutorId: courseToUpdate!.tutorId,
          start: updateWorkWeek(parsed('2025-01-10 08:15') as Timestamp),
          end: courseToUpdate!.end,
          roomId: courseToUpdate!.room,
          suppTutorIds: [55, 3],
          graded: false,
          roomTypeId: 3,
          groupIds: [422, 623, 552],
        },
        objectId: courseToUpdate!.id,
        type: 'course',
        operation: 'update',
      },
    ])
    expect(getDateTime(courseToUpdate!.start)).toBe('2025-01-10 08:15')
  })

  it('reverts an update of a course', () => {
    const scheduledCourseStore = useScheduledCourseStore()
    const { addUpdateBlock, revertUpdateBlock, hasUpdate } = useUndoredo()

    const courseToUpdate = scheduledCourseStore.getCourse(65692, '2023-04-25')

    addUpdateBlock([
      {
        data: {
          tutorId: courseToUpdate!.tutorId,
          start: parseTimestamp('2022-01-10 08:20') as Timestamp,
          end: courseToUpdate!.end,
          roomId: courseToUpdate!.room,
          suppTutorIds: courseToUpdate!.suppTutorIds,
          graded: courseToUpdate!.graded,
          roomTypeId: courseToUpdate!.roomTypeId,
          groupIds: courseToUpdate!.groupIds,
        },
        objectId: courseToUpdate!.id,
        type: 'course',
        operation: 'update',
      },
    ])

    revertUpdateBlock()

    expect(getDateTime(courseToUpdate!.start)).toBe('2023-04-25 14:15')
    expect(hasUpdate.value).toBe(false)
  })

  it('reverts several updates of a course', () => {
    const scheduledCourseStore = useScheduledCourseStore()
    const { addUpdateBlock, revertUpdateBlock, hasUpdate } = useUndoredo()

    const courseToUpdate = scheduledCourseStore.getCourse(65692, '2023-04-25')
    addUpdateBlock([
      {
        data: {
          tutorId: courseToUpdate!.tutorId,
          start: updateWorkWeek(parsed('2022-01-10 08:20') as Timestamp),
          end: courseToUpdate!.end,
          roomId: courseToUpdate?.room || -1,
          suppTutorIds: courseToUpdate!.suppTutorIds,
          graded: courseToUpdate!.graded,
          roomTypeId: courseToUpdate!.roomTypeId,
          groupIds: courseToUpdate!.groupIds,
        },
        objectId: courseToUpdate!.id,
        type: 'course',
        operation: 'update',
      },
    ])
    addUpdateBlock([
      {
        data: {
          tutorId: courseToUpdate!.tutorId,
          start: updateWorkWeek(parsed('2025-01-10 08:15') as Timestamp),
          end: courseToUpdate!.end,
          roomId: courseToUpdate?.room || -1,
          suppTutorIds: [],
          graded: false,
          roomTypeId: -1,
          groupIds: [],
        },
        objectId: courseToUpdate!.id,
        type: 'course',
        operation: 'update',
      },
    ])
    revertUpdateBlock()

    expect(getDateTime(courseToUpdate!.start)).toBe('2022-01-10 08:20')

    revertUpdateBlock()

    expect(getDateTime(courseToUpdate!.start)).toBe('2023-04-25 14:15')
    expect(hasUpdate.value).toBe(false)
  })

  it('historizes an update of an availability', () => {
    const availabilityStore = useAvailabilityStore()
    const { addUpdateBlock, hasUpdate } = useUndoredo()
    const availToUpdate = availabilityStore.getAvailability(23)
    addUpdateBlock([
      {
        data: {
          start: parseTimestamp('2022-01-25 14:00') as Timestamp,
          value: 1,
          duration: 60,
        },
        objectId: availToUpdate!.id,
        type: 'availability',
        operation: 'update',
      },
    ])
    expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 14:00')
    expect(availToUpdate!.value).toBe(1)
    expect(availToUpdate!.duration).toBe(60)
    expect(hasUpdate.value).toBe(true)

    addUpdateBlock([
      {
        objectId: availToUpdate!.id,
        data: {
          start: parseTimestamp('2023-04-22 16:00') as Timestamp,
          value: 7,
          duration: 150,
        },
        type: 'availability',
        operation: 'update',
      },
    ])
    expect(getDateTime(availToUpdate!.start)).toBe('2023-04-22 16:00')
    expect(availToUpdate!.value).toBe(7)
    expect(availToUpdate!.duration).toBe(150)
  })

  it('reverts an update of an availability', () => {
    const availabilityStore = useAvailabilityStore()
    const { addUpdateBlock, revertUpdateBlock, hasUpdate } = useUndoredo()
    const availToUpdate = availabilityStore.getAvailability(23)

    addUpdateBlock([
      {
        objectId: availToUpdate!.id,
        data: {
          start: parseTimestamp('2022-01-25 14:00') as Timestamp,
          value: 1,
          duration: 60,
        },
        type: 'availability',
        operation: 'update',
      },
    ])
    revertUpdateBlock()
    expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 14:10')
    expect(availToUpdate!.value).toBe(3)
    expect(availToUpdate!.duration).toBe(120)
    expect(hasUpdate.value).toBe(false)
  })

  it('reverts several updates of an availability', () => {
    const availabilityStore = useAvailabilityStore()
    const { addUpdateBlock, revertUpdateBlock } = useUndoredo()
    const availToUpdate = availabilityStore.getAvailability(23)
    addUpdateBlock([
      {
        data: {
          start: parseTimestamp('2022-01-25 14:00') as Timestamp,
          value: 1,
          duration: 60,
        },
        objectId: availToUpdate!.id,
        type: 'availability',
        operation: 'update',
      },
    ])
    addUpdateBlock([
      {
        data: {
          start: parseTimestamp('2022-01-25 08:00') as Timestamp,
          value: 0,
          duration: 90,
        },
        objectId: availToUpdate!.id,
        type: 'availability',
        operation: 'update',
      },
    ])
    revertUpdateBlock()
    expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 14:00')
    expect(availToUpdate!.value).toBe(1)
    expect(availToUpdate!.duration).toBe(60)
    revertUpdateBlock()
    expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 14:10')
    expect(availToUpdate!.value).toBe(3)
    expect(availToUpdate!.duration).toBe(120)
  })

  it('Stores Blocks of Availability updates', () => {
    const availabilityStore = useAvailabilityStore()
    const { addUpdateBlock, hasUpdate } = useUndoredo()
    const availToUpdate = availabilityStore.getAvailability(23)
    addUpdateBlock([
      {
        objectId: availToUpdate!.id,
        data: {
          start: parseTimestamp('2022-01-25 14:00') as Timestamp,
          value: 1,
          duration: 60,
        },
        type: 'availability',
        operation: 'update',
      },
      {
        data: {
          start: parseTimestamp('2022-01-25 12:00') as Timestamp,
          value: 8,
          duration: 30,
        },
        objectId: availToUpdate!.id,
        type: 'availability',
        operation: 'update',
      },
    ])
    expect(availToUpdate!.value).toBe(8)
    expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 12:00')
    expect(availToUpdate!.duration).toBe(30)
    addUpdateBlock([
      {
        objectId: availToUpdate!.id,
        data: {
          start: parseTimestamp('2022-01-25 10:00') as Timestamp,
          value: 5,
          duration: 25,
        },
        type: 'availability',
        operation: 'update',
      },
      {
        data: {
          start: parseTimestamp('2022-01-25 09:00') as Timestamp,
          value: 6,
          duration: 200,
        },
        objectId: availToUpdate!.id,
        type: 'availability',
        operation: 'update',
      },
      {
        data: {
          start: parseTimestamp('2022-01-25 07:00') as Timestamp,
          value: 2,
          duration: 100,
        },
        objectId: availToUpdate!.id,
        type: 'availability',
        operation: 'update',
      },
    ])
    expect(availToUpdate!.value).toBe(2)
    expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 07:00')
    expect(availToUpdate!.duration).toBe(100)
    expect(hasUpdate.value).toBe(true)
  })

  it('reverts blocks of Availability updates', () => {
    const availabilityStore = useAvailabilityStore()
    const { addUpdateBlock, revertUpdateBlock } = useUndoredo()
    const availToUpdate = availabilityStore.getAvailability(23)
    const updates: {
      data: CourseData | AvailabilityData
      objectId: number
      type: 'course' | 'availability'
      operation: 'update' | 'create' | 'remove'
    }[] = []
    updates.push({
      objectId: availToUpdate!.id,
      data: {
        start: parseTimestamp('2022-01-25 14:00') as Timestamp,
        value: 1,
        duration: 60,
      },
      type: 'availability',
      operation: 'update',
    })
    updates.push({
      data: {
        start: parseTimestamp('2022-01-25 12:00') as Timestamp,
        value: 8,
        duration: 30,
      },
      objectId: availToUpdate!.id,
      type: 'availability',
      operation: 'update',
    })
    addUpdateBlock(updates)
    addUpdateBlock([
      {
        objectId: availToUpdate!.id,
        data: {
          start: parseTimestamp('2022-01-25 10:00') as Timestamp,
          value: 5,
          duration: 25,
        },
        type: 'availability',
        operation: 'update',
      },
      {
        data: {
          start: parseTimestamp('2022-01-25 09:00') as Timestamp,
          value: 6,
          duration: 200,
        },
        objectId: availToUpdate!.id,
        type: 'availability',
        operation: 'update',
      },
      {
        data: {
          start: parseTimestamp('2022-01-25 07:00') as Timestamp,
          value: 2,
          duration: 100,
        },
        objectId: availToUpdate!.id,
        type: 'availability',
        operation: 'update',
      },
    ])
    revertUpdateBlock()
    expect(availToUpdate!.value).toBe(8)
    expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 12:00')
    expect(availToUpdate!.duration).toBe(30)
    revertUpdateBlock()
    expect(availToUpdate!.value).toBe(3)
    expect(getDateTime(availToUpdate!.start)).toBe('2022-01-25 14:10')
    expect(availToUpdate!.duration).toBe(120)
  })
  it('historizes the creation of an availability', () => {
    const availabilityStore = useAvailabilityStore()
    const { availabilities } = storeToRefs(availabilityStore)
    const { addUpdateBlock } = useUndoredo()
    addUpdateBlock([
      {
        objectId: 23,
        data: {
          start: parseTimestamp('2022-01-25 10:00') as Timestamp,
          value: 5,
          duration: 25,
        },
        type: 'availability',
        operation: 'create',
      },
    ])
    const newAvail = availabilityStore.getAvailability(1)
    const oldAvail = availabilityStore.getAvailability(23)
    const noAvail = availabilityStore.getAvailability(55)
    expect(availabilities.value.get('2022-01-25')?.length).toBe(2)
    expect(newAvail).toBeDefined()
    expect(oldAvail).toBeDefined()
    expect(noAvail).toBeUndefined()
  })
  it('historizes the creation of availabilities and revert them', () => {
    const availabilityStore = useAvailabilityStore()
    const { availabilities } = storeToRefs(availabilityStore)
    const { addUpdateBlock, revertUpdateBlock } = useUndoredo()
    addUpdateBlock([
      {
        objectId: 23,
        data: {
          start: parseTimestamp('2022-01-25 10:00') as Timestamp,
          value: 5,
          duration: 25,
        },
        type: 'availability',
        operation: 'create',
      },
      {
        objectId: 23,
        data: {
          start: parseTimestamp('2022-01-25 12:00') as Timestamp,
          value: 8,
          duration: 50,
        },
        type: 'availability',
        operation: 'update',
      },
      {
        objectId: 1,
        data: {
          start: parseTimestamp('2022-01-25 14:00') as Timestamp,
          value: 1,
          duration: 100,
        },
        type: 'availability',
        operation: 'create',
      },
    ])
    addUpdateBlock([
      {
        objectId: 2,
        data: {
          start: parseTimestamp('2022-01-26 22:00') as Timestamp,
          value: 2,
          duration: 75,
        },
        type: 'availability',
        operation: 'create',
      },
    ])
    expect(availabilities.value.get('2022-01-25')?.length).toBe(3)
    expect(availabilities.value.get('2022-01-26')?.length).toBe(1)
    revertUpdateBlock()
    expect(availabilities.value.get('2022-01-26')?.length).toBe(0)
    revertUpdateBlock()
    expect(availabilities.value.get('2022-01-25')?.length).toBe(1)
  })

  it('historizes the deletion of an availability', () => {
    const availabilityStore = useAvailabilityStore()
    const { availabilities } = storeToRefs(availabilityStore)
    const { addUpdateBlock, hasUpdate } = useUndoredo()
    addUpdateBlock([
      {
        objectId: 23,
        data: {
          start: parseTimestamp('2022-01-25 22:00') as Timestamp,
          value: 2,
          duration: 75,
          dataId: 23,
          availType: 'user',
        },
        type: 'availability',
        operation: 'remove',
      },
    ])
    expect(availabilities.value.get('2022-01-25')?.length).toBe(0)
    expect(hasUpdate.value).toBe(true)
  })
  it('historizes the deletion of availabilities and revert them', () => {
    const availabilityStore = useAvailabilityStore()
    const { availabilities } = storeToRefs(availabilityStore)
    const { addUpdateBlock, revertUpdateBlock } = useUndoredo()
    addUpdateBlock([
      {
        objectId: 23,
        data: {
          start: parseTimestamp('2022-01-26 23:00') as Timestamp,
          value: 2,
          duration: 75,
          dataId: 23,
          availType: 'user',
        },
        type: 'availability',
        operation: 'create',
      },
      {
        objectId: 23,
        data: {
          start: parseTimestamp('2022-01-25 22:00') as Timestamp,
          value: 2,
          duration: 75,
          dataId: 23,
          availType: 'user',
        },
        type: 'availability',
        operation: 'remove',
      },
      {
        objectId: 1,
        data: {
          start: parseTimestamp('2022-01-27 22:00') as Timestamp,
          value: 8,
          duration: 75,
          dataId: 23,
          availType: 'user',
        },
        type: 'availability',
        operation: 'update',
      },
    ])
    addUpdateBlock([
      {
        objectId: 1,
        data: {
          start: parseTimestamp('2022-01-26 23:00') as Timestamp,
          value: 2,
          duration: 75,
          dataId: 23,
          availType: 'user',
        },
        type: 'availability',
        operation: 'remove',
      },
    ])
    expect(availabilities.value.get('2022-01-25')?.length).toBe(0)
    revertUpdateBlock()
    expect(availabilities.value.get('2022-01-27')?.length).toBe(1)
    revertUpdateBlock()
    expect(availabilities.value.get('2022-01-25')?.length).toBe(1)
  })

  it('historizes the deletion of a course', () => {
    const courseStore = useScheduledCourseStore()
    const { addUpdateBlock, hasUpdate } = useUndoredo()
    addUpdateBlock([
      {
        objectId: 65692,
        data: {
          tutorId: -1,
          start: parseTimestamp(today())!,
          end: parseTimestamp(today())!,
          roomId: -1,
          suppTutorIds: [],
          graded: false,
          roomTypeId: -1,
          groupIds: [],
        },
        type: 'course',
        operation: 'remove',
      },
    ])
    expect(courseStore.getCourse(65692)).toBeUndefined()
    expect(hasUpdate.value).toBe(true)
  })

  it('historizes the deletion of a course and revert it', () => {
    const courseStore = useScheduledCourseStore()
    const { addUpdateBlock, revertUpdateBlock, hasUpdate } = useUndoredo()
    addUpdateBlock([
      {
        objectId: 65692,
        data: {
          tutorId: -1,
          start: parseTimestamp(today())!,
          end: parseTimestamp(today())!,
          roomId: -1,
          suppTutorIds: [],
          graded: false,
          roomTypeId: -1,
          groupIds: [],
        },
        type: 'course',
        operation: 'remove',
      },
    ])
    expect(courseStore.getCourse(65692)).toBeUndefined()
    expect(hasUpdate.value).toBe(true)
    revertUpdateBlock()
    expect(courseStore.getCourse(65692)).toBeDefined()
    expect(hasUpdate.value).toBe(false)
  })
})
