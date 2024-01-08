import { Timestamp, parseTimestamp } from '@quasar/quasar-ui-qcalendar'
import { beforeEach, describe, expect, it } from 'vitest'
import { useAvailabilityStore } from './availability'
import { createPinia, setActivePinia } from 'pinia'
import { Availability } from '../declarations'
import { AvailabilityBack } from '@/ts/type'

describe('Availibility store utils', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  it('Transforms an Availibility in back Availability', () => {
    expect.assertions(12)
    const availabilityStore = useAvailabilityStore()
    let availability: Availability = {
      id: 1,
      duration: 20,
      start: parseTimestamp('2023-10-14 14:30') as Timestamp,
      value: 3,
      type: 'user',
      dataId: 40,
    }
    const availabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(availabilityBack.id).toBe(1)
    expect(availabilityBack.value).toBe(3)
    expect(availabilityBack.start_time.getDay()).toBe(6)
    expect(availabilityBack.start_time.getDate()).toBe(14)
    expect(availabilityBack.start_time.getHours()).toBe(14)
    expect(availabilityBack.start_time.getMinutes()).toBe(30)
    expect(availabilityBack.av_type).toBe('user')
    expect(availabilityBack.dataId).toBe(40)
    expect(availabilityBack.end_time.getDay()).toBe(6)
    expect(availabilityBack.end_time.getDate()).toBe(14)
    expect(availabilityBack.end_time.getHours()).toBe(14)
    expect(availabilityBack.end_time.getMinutes()).toBe(50)
  })

  it('Transforms a back Availability in Availability', () => {
    expect.assertions(8)
    const availabilityStore = useAvailabilityStore()
    let availabilityBack: AvailabilityBack = {
      id: 1,
      start_time: new Date('2017-01-15 14:30'),
      end_time: new Date('2017-01-15 18:00'),
      value: 0,
      av_type: 'user',
      dataId: 10,
    }

    const availability = availabilityStore.availabilityBackToAvailability(availabilityBack)
    expect(availability.start).toStrictEqual(parseTimestamp('2017-01-15 14:30') as Timestamp)
    expect(availability.start.day).toBe(15)
    expect(availability.start.weekday).toBe(0)
    expect(availability.duration).toBe(210)
    expect(availability.id).toBe(1)
    expect(availability.value).toBe(0)
    expect(availability.dataId).toBe(10)
    expect(availability.type).toBe('user')
  })

  it('Transforms an Availibility in back Availability and back', () => {
    expect.assertions(20)
    const availabilityStore = useAvailabilityStore()
    let availability: Availability = {
      id: 9,
      duration: 60,
      start: parseTimestamp('2020-05-01 14:30') as Timestamp,
      value: 3,
      type: 'user',
      dataId: 22,
    }
    const availabilityBack: AvailabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(availabilityBack.end_time.getDay()).toBe(5)
    expect(availabilityBack.end_time.getDate()).toBe(1)
    expect(availabilityBack.end_time.getHours()).toBe(15)
    expect(availabilityBack.end_time.getMinutes()).toBe(30)
    expect(availabilityBack.id).toBe(9)
    expect(availabilityBack.value).toBe(3)
    expect(availabilityBack.start_time.getDay()).toBe(5)
    expect(availabilityBack.start_time.getDate()).toBe(1)
    expect(availabilityBack.start_time.getHours()).toBe(14)
    expect(availabilityBack.start_time.getMinutes()).toBe(30)
    expect(availabilityBack.av_type).toBe('user')
    expect(availabilityBack.dataId).toBe(22)

    const newAvailability = availabilityStore.availabilityBackToAvailability(availabilityBack)
    expect(newAvailability.start).toStrictEqual(parseTimestamp('2020-05-01 14:30') as Timestamp)
    expect(newAvailability.start.day).toBe(1)
    expect(newAvailability.start.weekday).toBe(5)
    expect(newAvailability.duration).toBe(60)
    expect(newAvailability.id).toBe(9)
    expect(newAvailability.value).toBe(3)
    expect(newAvailability.dataId).toBe(22)
    expect(newAvailability.type).toBe('user')
  })

  it('Transforms a back Availability in Availability and back', () => {
    expect.assertions(20)
    const availabilityStore = useAvailabilityStore()
    let availabilityBack: AvailabilityBack = {
      id: 1,
      start_time: new Date('2017-01-15 14:30'),
      end_time: new Date('2017-01-15 18:00'),
      value: 0,
      av_type: 'user',
      dataId: 10,
    }

    const availability = availabilityStore.availabilityBackToAvailability(availabilityBack)
    expect(availability.start).toStrictEqual(parseTimestamp('2017-01-15 14:30') as Timestamp)
    expect(availability.start.day).toBe(15)
    expect(availability.start.weekday).toBe(0)
    expect(availability.duration).toBe(210)
    expect(availability.id).toBe(1)
    expect(availability.value).toBe(0)
    expect(availability.dataId).toBe(10)
    expect(availability.type).toBe('user')

    const newAvailabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(newAvailabilityBack.end_time.getDay()).toBe(0)
    expect(newAvailabilityBack.end_time.getDate()).toBe(15)
    expect(newAvailabilityBack.end_time.getHours()).toBe(18)
    expect(newAvailabilityBack.end_time.getMinutes()).toBe(0)
    expect(newAvailabilityBack.id).toBe(1)
    expect(newAvailabilityBack.value).toBe(0)
    expect(newAvailabilityBack.start_time.getDay()).toBe(0)
    expect(newAvailabilityBack.start_time.getDate()).toBe(15)
    expect(newAvailabilityBack.start_time.getHours()).toBe(14)
    expect(newAvailabilityBack.start_time.getMinutes()).toBe(30)
    expect(newAvailabilityBack.av_type).toBe('user')
    expect(newAvailabilityBack.dataId).toBe(10)
  })
})
