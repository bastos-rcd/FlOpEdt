import { AvailabilityBack } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Availability } from '../declarations'
import {
  Timestamp,
  copyTimestamp,
  getDateTime,
  parseTime,
  parseTimestamp,
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
    let dateString: string = preference.start.getFullYear() + '-'
    if (preference.start.getMonth() < 9) dateString += '0'
    dateString += preference.start.getMonth() + 1 + '-'
    if (preference.start.getDate() < 10) dateString += '0'
    dateString += preference.start.getDate() + ' '
    if (preference.start.getHours() < 10) dateString += '0'
    dateString += preference.start.getHours() + ':'
    if (preference.start.getMinutes() < 10) dateString += '0'
    dateString += preference.start.getMinutes()
    let start: Timestamp = parseTimestamp(dateString) as Timestamp

    let newAvailability: Availability = {
      id: preference.id,
      type: preference.type,
      //@ts-expect-error
      duration: (preference.end - preference.start) / 1000 / 60,
      start: start,
      value: preference.value,
      dataId: preference.dataId,
    }
    return newAvailability
  }

  function availabilityToPreference(availability: Availability): AvailabilityBack {
    let startCopy = copyTimestamp(availability.start)
    let newPreference: AvailabilityBack = {
      id: availability.id,
      start: new Date(getDateTime(availability.start)),
      end: new Date(getDateTime(updateMinutes(startCopy, availability.duration + parseTime(startCopy)))),
      value: availability.value,
      type: availability.type,
      dataId: availability.dataId,
    }
    return newPreference
  }

  return {
    availabilityToPreference,
    preferenceToAvailability,
    fetchUserPreferences,
  }
})
