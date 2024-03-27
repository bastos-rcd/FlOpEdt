import { Timestamp, parseTime, parseTimestamp } from '@quasar/quasar-ui-qcalendar'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAvailabilityStore } from './availability'
import { createPinia, setActivePinia } from 'pinia'
import { Availability } from '../declarations'
import { AvailabilityBack } from '@/ts/type'
import { usePermanentStore } from './permanent'

vi.mock('./permanent.ts')
vi.mock('./department.ts')

describe('Availibility store utils', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const permanentStore = usePermanentStore()
    const availabilityStore = useAvailabilityStore()
    void permanentStore.fetchTimeSettings()
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

    availabilityStore.addOrUpdateAvailibility({
      id: 33,
      duration: 1440,
      start: parseTimestamp('2024-03-27 00:00')!,
      value: 4,
      type: 'user',
      dataId: 22,
    })
    availabilityStore.addOrUpdateAvailibility({
      id: 34,
      duration: 420,
      start: parseTimestamp('2024-03-27 00:00')!,
      value: 4,
      type: 'user',
      dataId: 22,
    })
    availabilityStore.addOrUpdateAvailibility({
      id: 35,
      duration: 200,
      start: parseTimestamp('2024-03-27 00:00')!,
      value: 4,
      type: 'user',
      dataId: 22,
    })
    availabilityStore.addOrUpdateAvailibility({
      id: 36,
      duration: 720,
      start: parseTimestamp('2024-03-27 12:00')!,
      value: 4,
      type: 'user',
      dataId: 22,
    })
    availabilityStore.addOrUpdateAvailibility({
      id: 37,
      duration: 120,
      start: parseTimestamp('2024-03-27 19:00')!,
      value: 4,
      type: 'user',
      dataId: 22,
    })

    availabilityStore.addOrUpdateAvailibility({
      id: 38,
      duration: 120,
      start: parseTimestamp('2024-03-27 12:00')!,
      value: 4,
      type: 'user',
      dataId: 22,
    })
  })

  it("gets an item from the store if it's presents or returns undefined value", () => {
    const availabilityStore = useAvailabilityStore()
    const availability = availabilityStore.getAvailability(1)
    expect(availabilityStore.availabilities.size).toBe(3)
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
    const availabilityBack: AvailabilityBack = {
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
    const availability: Availability = availabilityStore.getAvailability(2)!
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
    const availabilityBack: AvailabilityBack = {
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

  it('Splits a back avail when it starts before daytime', () => {
    const permanentStore = usePermanentStore()
    expect(permanentStore.timeSettings.get(-1)).toBeDefined()
    const availabilityStore = useAvailabilityStore()
    const availAllDay = availabilityStore.getAvailability(33)
    const availOnStartDay = availabilityStore.getAvailability(34)
    const availBeforeStartDay = availabilityStore.getAvailability(35)
    const availOnEndDay = availabilityStore.getAvailability(36)
    const availAfterEndDay = availabilityStore.getAvailability(37)
    const availDuringDay = availabilityStore.getAvailability(38)
    expect(availAllDay).toBeDefined()
    expect(availOnStartDay).toBeDefined()
    expect(availBeforeStartDay).toBeDefined()
    expect(availOnEndDay).toBeDefined()
    expect(availAfterEndDay).toBeDefined()
    expect(availDuringDay).toBeDefined()
    const fragmentedAvail = availabilityStore.formatAvailabilityWithDayTime(availAllDay!)
    expect(fragmentedAvail.length).toBe(3)
    expect(fragmentedAvail.find((av) => parseTime(av.start) === 0)?.duration).toBe(360)
    expect(fragmentedAvail.find((av) => parseTime(av.start) === 360)?.duration).toBe(720)
    expect(fragmentedAvail.find((av) => parseTime(av.start) === 1080)?.duration).toBe(360)
    const fragmentedAvail2 = availabilityStore.formatAvailabilityWithDayTime(availOnStartDay!)
    expect(fragmentedAvail2.length).toBe(2)
    expect(fragmentedAvail2.find((av) => parseTime(av.start) === 0)?.duration).toBe(360)
    expect(fragmentedAvail2.find((av) => parseTime(av.start) === 360)?.duration).toBe(60)
    const fragmentedAvail3 = availabilityStore.formatAvailabilityWithDayTime(availBeforeStartDay!)
    expect(fragmentedAvail3.length).toBe(1)
    expect(fragmentedAvail3.find((av) => parseTime(av.start) === 0)?.duration).toBe(200)
    const fragmentedAvail4 = availabilityStore.formatAvailabilityWithDayTime(availOnEndDay!)
    expect(fragmentedAvail2.length).toBe(2)
    expect(fragmentedAvail4.find((av) => parseTime(av.start) === 720)?.duration).toBe(360)
    expect(fragmentedAvail4.find((av) => parseTime(av.start) === 1080)?.duration).toBe(360)
    const fragmentedAvail5 = availabilityStore.formatAvailabilityWithDayTime(availAfterEndDay!)
    expect(fragmentedAvail5.length).toBe(1)
    expect(fragmentedAvail5.find((av) => parseTime(av.start) === 1140)?.duration).toBe(120)
    const fragmentedAvail6 = availabilityStore.formatAvailabilityWithDayTime(availDuringDay!)
    expect(fragmentedAvail6.length).toBe(1)
    expect(fragmentedAvail6.find((av) => parseTime(av.start) === 720)?.duration).toBe(120)
  })
})
