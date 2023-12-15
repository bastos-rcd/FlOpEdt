import { AvailabilityBack } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Availability } from '../declarations'
import {
  Timestamp,
  copyTimestamp,
  getTime,
  makeDateTime,
  parseDate,
  parseTime,
  updateMinutes,
} from '@quasar/quasar-ui-qcalendar'
import { api } from '@/utils/api'

export const useAvailabilityStore = defineStore('availabilityStore', () => {
  const preferences = ref<AvailabilityBack[]>([])
  const availabilities = ref<Availability[]>([])
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchUserPreferences(userId: number, week: number, year: number): Promise<void> {
    isLoading.value = true
    try {
      await api.getPreferencesForWeek(userId, week, year).then((result) => {
        preferences.value = result
        isLoading.value = false
        preferences.value.forEach((pref) => {
          availabilities.value.push(preferenceToAvailability(pref))
        })
      })
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  function preferenceToAvailability(preference: AvailabilityBack): Availability {
    console.log('preference offSet: ', preference.start.getTimezoneOffset())
    let newAvailability: Availability = {
      id: preference.id,
      type: preference.type,
      //@ts-expect-error
      duration: (preference.end - preference.start) / 1000 / 60,
      start: parseDate(preference.start) as Timestamp,
      value: preference.value,
      dataId: preference.dataId,
    }
    updateMinutes(
      newAvailability.start,
      parseTime(getTime(newAvailability.start)) + preference.start.getTimezoneOffset()
    )
    console.log('preference : ', preference)
    console.log('newAvailability : ', newAvailability)
    return newAvailability
  }

  function availabilityToPreference(availability: Availability): AvailabilityBack {
    let startCopy = copyTimestamp(availability.start)
    let newPreference: AvailabilityBack = {
      id: availability.id,
      start: makeDateTime(availability.start),
      end: makeDateTime(updateMinutes(startCopy, availability.duration + parseTime(availability.start))),
      value: availability.value,
      type: availability.type,
      dataId: availability.dataId,
    }
    console.log('availability : ', availability)
    console.log('newPreference : ', newPreference.start.getTimezoneOffset())
    return newPreference
  }

  return {
    availabilityToPreference,
    preferenceToAvailability,
    fetchUserPreferences,
  }
})
