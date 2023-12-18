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
  it('Transforms an Availibility in Preference', () => {
    expect.assertions(12)
    const availabilityStore = useAvailabilityStore()
    let availability: Availability = {
      id: 1,
      duration: 20,
      start: parseTimestamp('2023-10-14 14:30') as Timestamp,
      value: 3,
      type: 'userPref',
      dataId: 40,
    }
    const availabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(availabilityBack.id).toBe(1)
    expect(availabilityBack.value).toBe(3)
    expect(availabilityBack.start.getDay()).toBe(6)
    expect(availabilityBack.start.getDate()).toBe(14)
    expect(availabilityBack.start.getHours()).toBe(14)
    expect(availabilityBack.start.getMinutes()).toBe(30)
    expect(availabilityBack.type).toBe('userPref')
    expect(availabilityBack.dataId).toBe(40)
    expect(availabilityBack.end.getDay()).toBe(6)
    expect(availabilityBack.end.getDate()).toBe(14)
    expect(availabilityBack.end.getHours()).toBe(14)
    expect(availabilityBack.end.getMinutes()).toBe(50)
  })

  it('Transforms a Preference in Availability', () => {
    expect.assertions(8)
    const availabilityStore = useAvailabilityStore()
    let preference: AvailabilityBack = {
      id: 1,
      start: new Date('2017-01-15 14:30'),
      end: new Date('2017-01-15 18:00'),
      value: 0,
      type: 'userPref',
      dataId: 10,
    }

    const availability = availabilityStore.availabilityBackToAvailability(preference)
    expect(availability.start).toStrictEqual(parseTimestamp('2017-01-15 14:30') as Timestamp)
    expect(availability.start.day).toBe(15)
    expect(availability.start.weekday).toBe(0)
    expect(availability.duration).toBe(210)
    expect(availability.id).toBe(1)
    expect(availability.value).toBe(0)
    expect(availability.dataId).toBe(10)
    expect(availability.type).toBe('userPref')
  })

  it('Transforms an Availibility in Preference and back', () => {
    expect.assertions(20)
    const availabilityStore = useAvailabilityStore()
    let availability: Availability = {
      id: 9,
      duration: 60,
      start: parseTimestamp('2020-05-01 14:30') as Timestamp,
      value: 3,
      type: 'userPref',
      dataId: 22,
    }
    const availabilityBack: AvailabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(availabilityBack.end.getDay()).toBe(5)
    expect(availabilityBack.end.getDate()).toBe(1)
    expect(availabilityBack.end.getHours()).toBe(15)
    expect(availabilityBack.end.getMinutes()).toBe(30)
    expect(availabilityBack.id).toBe(9)
    expect(availabilityBack.value).toBe(3)
    expect(availabilityBack.start.getDay()).toBe(5)
    expect(availabilityBack.start.getDate()).toBe(1)
    expect(availabilityBack.start.getHours()).toBe(14)
    expect(availabilityBack.start.getMinutes()).toBe(30)
    expect(availabilityBack.type).toBe('userPref')
    expect(availabilityBack.dataId).toBe(22)

    const newAvailability = availabilityStore.availabilityBackToAvailability(availabilityBack)
    expect(newAvailability.start).toStrictEqual(parseTimestamp('2020-05-01 14:30') as Timestamp)
    expect(newAvailability.start.day).toBe(1)
    expect(newAvailability.start.weekday).toBe(5)
    expect(newAvailability.duration).toBe(60)
    expect(newAvailability.id).toBe(9)
    expect(newAvailability.value).toBe(3)
    expect(newAvailability.dataId).toBe(22)
    expect(newAvailability.type).toBe('userPref')
  })

  it('Transforms a Preference in Availability and back', () => {
    expect.assertions(20)
    const availabilityStore = useAvailabilityStore()
    let preference: AvailabilityBack = {
      id: 1,
      start: new Date('2017-01-15 14:30'),
      end: new Date('2017-01-15 18:00'),
      value: 0,
      type: 'userPref',
      dataId: 10,
    }

    const availability = availabilityStore.availabilityBackToAvailability(preference)
    expect(availability.start).toStrictEqual(parseTimestamp('2017-01-15 14:30') as Timestamp)
    expect(availability.start.day).toBe(15)
    expect(availability.start.weekday).toBe(0)
    expect(availability.duration).toBe(210)
    expect(availability.id).toBe(1)
    expect(availability.value).toBe(0)
    expect(availability.dataId).toBe(10)
    expect(availability.type).toBe('userPref')

    const newAvailabilityBack = availabilityStore.availabilityToAvailabilityBack(availability)
    expect(newAvailabilityBack.end.getDay()).toBe(0)
    expect(newAvailabilityBack.end.getDate()).toBe(15)
    expect(newAvailabilityBack.end.getHours()).toBe(18)
    expect(newAvailabilityBack.end.getMinutes()).toBe(0)
    expect(newAvailabilityBack.id).toBe(1)
    expect(newAvailabilityBack.value).toBe(0)
    expect(newAvailabilityBack.start.getDay()).toBe(0)
    expect(newAvailabilityBack.start.getDate()).toBe(15)
    expect(newAvailabilityBack.start.getHours()).toBe(14)
    expect(newAvailabilityBack.start.getMinutes()).toBe(30)
    expect(newAvailabilityBack.type).toBe('userPref')
    expect(newAvailabilityBack.dataId).toBe(10)
  })
})
