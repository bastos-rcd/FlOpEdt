import { Timestamp, parseTimestamp } from '@quasar/quasar-ui-qcalendar'
import { beforeEach, describe, expect, it } from 'vitest'
import { useAvailabilityStore } from './availability'
import { createPinia, setActivePinia } from 'pinia'
import { Availability } from '../declarations'
import { AvailabilityBack } from '@/ts/type'

describe('Availibility store utils', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const availabilityStore = useAvailabilityStore()
    availabilityStore.addOrUpdateAvailibilityEvent(
      {
        id: -1,
        title: '1',

        toggled: true,

        bgcolor: 'blue',

        data: {
          dataId: 40,
          dataType: 'avail',
          start: parseTimestamp('2023-10-14 14:30') as Timestamp,
          duration: 20,
          value: 3,
        },
        columnIds: [],
      },
      40,
      'user'
    )

    availabilityStore.addOrUpdateAvailibilityEvent(
      {
        id: -1,
        title: '9',

        toggled: true,

        bgcolor: 'blue',

        data: {
          dataId: 22,
          dataType: 'avail',
          start: parseTimestamp('2020-05-01 14:30') as Timestamp,
          duration: 60,
          value: 3,
        },
        columnIds: [],
      },
      22,
      'user'
    )
  })

  it("gets an item from the store if it's presents or returns undefined value", () => {
    const availabilityStore = useAvailabilityStore()
    const availability = availabilityStore.getAvailability(1)
    expect(availabilityStore.availabilities.size).toBe(2)
    const notExistentAvailability = availabilityStore.getAvailability(120)
    const availabilitiesOnDate = availabilityStore.getAvailabilityFromDates([parseTimestamp('2020-05-01')!])
    expect(availabilitiesOnDate).toBeDefined()
    expect(availabilitiesOnDate.length).toBe(1)
    expect(availability).toBeDefined()
    expect(notExistentAvailability).toBeUndefined()
  })

  it('Transforms an Availibility in back Availability', () => {
    expect.assertions(4)
    const availabilityStore = useAvailabilityStore()
    const availability: Availability = availabilityStore.getAvailability(1)!
    expect(availability)?.toBeDefined()
    const availabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(availabilityBack.value).toBe(3)
    expect(availabilityBack.av_type).toBe('user')
    expect(availabilityBack.dataId).toBe(40)
  })

  it('Transforms a back Availability in Availability', () => {
    expect.assertions(7)
    const availabilityStore = useAvailabilityStore()
    let availabilityBack: AvailabilityBack = {
      start_time: parseTimestamp('2017-01-15 14:30'),
      duration: '03:30:00',
      value: 0,
      av_type: 'user',
      dataId: 10,
    }

    const availability = availabilityStore.availabilityBackToAvailability(availabilityBack)
    expect(availability.start).toStrictEqual(parseTimestamp('2017-01-15 14:30') as Timestamp)
    expect(availability.start.day).toBe(15)
    expect(availability.start.weekday).toBe(0)
    expect(availability.duration).toBe(210)
    expect(availability.value).toBe(0)
    expect(availability.dataId).toBe(10)
    expect(availability.type).toBe('user')
  })

  it('Transforms an Availibility in back Availability and back', () => {
    expect.assertions(10)
    const availabilityStore = useAvailabilityStore()
    let availability: Availability = availabilityStore.getAvailability(2)!
    const availabilityBack: AvailabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(availabilityBack.value).toBe(3)
    expect(availabilityBack.av_type).toBe('user')
    expect(availabilityBack.dataId).toBe(22)

    const newAvailability = availabilityStore.availabilityBackToAvailability(availabilityBack)
    expect(newAvailability.start).toStrictEqual(parseTimestamp('2020-05-01 14:30') as Timestamp)
    expect(newAvailability.start.day).toBe(1)
    expect(newAvailability.start.weekday).toBe(5)
    expect(newAvailability.duration).toBe(60)
    expect(newAvailability.value).toBe(3)
    expect(newAvailability.dataId).toBe(22)
    expect(newAvailability.type).toBe('user')
  })

  it('Transforms a back Availability in Availability and back', () => {
    expect.assertions(10)
    const availabilityStore = useAvailabilityStore()
    let availabilityBack: AvailabilityBack = {
      start_time: parseTimestamp('2017-01-15 14:30'),
      duration: '03:30:00',
      value: 0,
      av_type: 'user',
      dataId: 10,
    }

    const availability = availabilityStore.availabilityBackToAvailability(availabilityBack)
    expect(availability.start).toStrictEqual(parseTimestamp('2017-01-15 14:30') as Timestamp)
    expect(availability.start.day).toBe(15)
    expect(availability.start.weekday).toBe(0)
    expect(availability.duration).toBe(210)
    expect(availability.value).toBe(0)
    expect(availability.dataId).toBe(10)
    expect(availability.type).toBe('user')

    const newAvailabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(newAvailabilityBack.value).toBe(0)
    expect(newAvailabilityBack.av_type).toBe('user')
    expect(newAvailabilityBack.dataId).toBe(10)
  })
})
