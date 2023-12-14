import { Timestamp, getTime, parseTime, parseTimestamp } from '@quasar/quasar-ui-qcalendar'
import { beforeEach, describe, expect, it } from 'vitest'
import { useAvailabilityStore } from './availability'
import { createPinia, setActivePinia } from 'pinia'
import { Availability } from '../declarations'
import { Preference } from '@/ts/type'

describe('Availibility store utils', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  it('Transforms an Availibility in Preference', () => {
    expect.assertions(6)
    const availabilityStore = useAvailabilityStore()
    let availability: Availability = {
      id: 1,
      duration: 20,
      start: parseTimestamp('2023-10-14 14:30') as Timestamp,
      value: 3,
    }
    const preference = availabilityStore.availabilityToPreference(availability)
    expect(preference.day).toBe('sa')
    expect(preference.duration).toBe(availability.duration)
    expect(preference.id).toBe(availability.id)
    expect(preference.value).toBe(availability.value)
    expect(preference.startTimeMinutes).toBe(parseTime(getTime(availability.start)))
    expect(preference.week).toBe(41)
  })

  it('Transforms a Preference in Availability', () => {
    expect.assertions(6)
    const availabilityStore = useAvailabilityStore()
    let preference: Preference = {
      id: 1,
      startTimeMinutes: 870,
      duration: 210,
      week: 2,
      day: 'su',
      value: 0,
    }

    const availability = availabilityStore.preferenceToAvailability(preference, 2017)
    expect(availability.start).toStrictEqual(parseTimestamp('2017-01-15 14:30') as Timestamp)
    expect(availability.start.day).toBe(15)
    expect(availability.start.weekday).toBe(0)
    expect(availability.duration).toBe(preference.duration)
    expect(availability.id).toBe(preference.id)
    expect(availability.value).toBe(preference.value)
  })

  it('Transforms an Availibility in Preference and back', () => {
    expect.assertions(12)
    const availabilityStore = useAvailabilityStore()
    let availability: Availability = {
      id: 1,
      duration: 20,
      start: parseTimestamp('2020-05-01 14:30') as Timestamp,
      value: 3,
    }
    const preference = availabilityStore.availabilityToPreference(availability)
    expect(preference.day).toBe('f')
    expect(preference.duration).toBe(availability.duration)
    expect(preference.id).toBe(availability.id)
    expect(preference.value).toBe(availability.value)
    expect(preference.startTimeMinutes).toBe(parseTime(getTime(availability.start)))
    expect(preference.week).toBe(18)

    const newAvailability = availabilityStore.preferenceToAvailability(preference, 2020)
    expect(newAvailability.start).toStrictEqual(parseTimestamp('2020-05-01 14:30') as Timestamp)
    expect(newAvailability.start.day).toBe(1)
    expect(newAvailability.start.weekday).toBe(5)
    expect(newAvailability.duration).toBe(preference.duration)
    expect(newAvailability.id).toBe(preference.id)
    expect(newAvailability.value).toBe(preference.value)
  })
})
