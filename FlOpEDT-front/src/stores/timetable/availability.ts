import { Preference } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Availability } from '../declarations'
import { getDateFromWeekDayOfWeekYear, getDayOfWeek, getDayOfWeekString } from '@/helpers'
import { Timestamp, getWeekday, getWorkWeek, parseDate, parseTime } from '@quasar/quasar-ui-qcalendar'
import { api } from '@/utils/api'

export const useAvailabilityStore = defineStore('availabilityStore', () => {
  const preferences = ref<Preference[]>([])
  const availabilities = ref<Availability[]>([])
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchUserPreferences(userName: string = '', week: number, year: number): Promise<void> {
    isLoading.value = true
    try {
      await api.getPreferencesForWeek(userName, week, year).then((result) => {
        preferences.value = result
        preferences.value.forEach(pref => {
          if(!pref.week) pref.week = week
          if(!pref.year) pref.year = year
        })
        isLoading.value = false
        preferences.value.forEach((pref) => {
          availabilities.value.push(preferenceToAvailability(pref))
        })
      })
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  function preferenceToAvailability(preference: Preference): Availability {
    if (!preference.year) preference.year = new Date().getFullYear()
    let newAvailability: Availability = {
      id: preference.id,
      type: preference.type,
      duration: preference.duration,
      start: parseDate(
        getDateFromWeekDayOfWeekYear(preference.week, getDayOfWeek(preference.day), preference.startTimeMinutes, preference.year)
      ) as Timestamp,
      value: preference.value,
      userName: preference.userName,
      //dataId: preference.dataId,
    }
    return newAvailability
  }

  function availabilityToPreference(availability: Availability): Preference {
    let newPreference: Preference = {
      id: availability.id,
      startTimeMinutes: parseTime(availability.start),
      duration: availability.duration,
      week: getWorkWeek(availability.start),
      day: getDayOfWeekString(getWeekday(availability.start)),
      value: availability.value,
      type: availability.type,
      //dataId: availability.dataId,
      userName: availability.userName,
      year: availability.start.year,
    }
    return newPreference
  }

  return {
    availabilityToPreference,
    preferenceToAvailability,
    fetchUserPreferences
  }
})
