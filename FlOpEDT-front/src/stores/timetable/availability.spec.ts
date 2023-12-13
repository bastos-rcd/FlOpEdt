import { Timestamp, getTime, parseTime, parseTimestamp } from '@quasar/quasar-ui-qcalendar'
import { assert, beforeEach, describe, expect, it } from 'vitest'
import { useAvailabilityStore } from './availability'
import { createPinia, setActivePinia } from 'pinia'
import { Availability } from '../declarations'
import { Preference } from '@/ts/type'
import { getDayOfWeekString } from '@/helpers'

describe('Availibility store utils', () => {
  beforeEach(() => {
    // creates a fresh pinia and make it active so it's automatically picked
    // up by any useStore() call without having to pass it to it:
    // `useStore(pinia)`
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
      week: 41,
      day: 'sa',
      value: 0,
    }

    const availability = availabilityStore.preferenceToAvailability(preference)
    expect(availability.start).toStrictEqual(parseTimestamp('2023-10-14 14:30') as Timestamp)
    expect(availability.start.day).toBe(14)
    expect(availability.start.weekday).toBe(6)
    expect(availability.duration).toBe(preference.duration)
    expect(availability.id).toBe(preference.id)
    expect(availability.value).toBe(preference.value)
  })
})
