import { Preference } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Availability } from '../declarations'
import { getDateFromWeekDayOfWeekYear, getDayOfWeek, getDayOfWeekString } from '@/helpers'
import { Timestamp, getWeekday, getWorkWeek, parseDate, parseTime } from '@quasar/quasar-ui-qcalendar'

export const useAvailabilityStore = defineStore('availabilityStore', () => {
  const preferences = ref<Preference[]>([])
  const availabilities = ref<Availability[]>([])

  function fetchPreferences(): void {}

  function preferenceToAvailability(preference: Preference): Availability {
    let newAvailability: Availability = {
      id: preference.id,
      duration: preference.duration,
      start: parseDate(
        getDateFromWeekDayOfWeekYear(preference.week, getDayOfWeek(preference.day), preference.startTimeMinutes)
      ) as Timestamp,
      value: preference.value,
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
    }
    return newPreference
  }

  return {
    availabilityToPreference,
    preferenceToAvailability,
  }
})
