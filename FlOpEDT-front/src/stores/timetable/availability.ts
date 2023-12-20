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
  const availabilitiesBack = ref<AvailabilityBack[]>([])
  const availabilities = ref<Availability[]>([])
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchUserPreferences(userId: number, week: number, year: number): Promise<void> {
    isLoading.value = true
    try {
      await api.getPreferencesForWeek(userId, week, year).then((result) => {
        availabilitiesBack.value = result
        isLoading.value = false
        availabilitiesBack.value.forEach((availabilityBack) => {
          availabilities.value.push(availabilityBackToAvailability(availabilityBack))
        })
      })
    } catch (e) {
      loadingError.value = e as Error
      isLoading.value = false
    }
  }

  function availabilityBackToAvailability(availabilityBack: AvailabilityBack): Availability {
    let dateString: string = availabilityBack.start.getFullYear() + '-'
    if (availabilityBack.start.getMonth() < 9) dateString += '0'
    dateString += availabilityBack.start.getMonth() + 1 + '-'
    if (availabilityBack.start.getDate() < 10) dateString += '0'
    dateString += availabilityBack.start.getDate() + ' '
    if (availabilityBack.start.getHours() < 10) dateString += '0'
    dateString += availabilityBack.start.getHours() + ':'
    if (availabilityBack.start.getMinutes() < 10) dateString += '0'
    dateString += availabilityBack.start.getMinutes()
    let start: Timestamp = parseTimestamp(dateString) as Timestamp

    let newAvailability: Availability = {
      id: availabilityBack.id,
      type: availabilityBack.type,
      //@ts-expect-error
      duration: (availabilityBack.end - availabilityBack.start) / 1000 / 60,
      start: start,
      value: availabilityBack.value,
      dataId: availabilityBack.dataId,
    }
    return newAvailability
  }

  function availabilityToAvailabilityBack(availability: Availability): AvailabilityBack {
    let startCopy = copyTimestamp(availability.start)
    let newAvailabilityBack: AvailabilityBack = {
      id: availability.id,
      start: new Date(getDateTime(availability.start)),
      end: new Date(getDateTime(updateMinutes(startCopy, availability.duration + parseTime(startCopy)))),
      value: availability.value,
      type: availability.type,
      dataId: availability.dataId,
    }
    return newAvailabilityBack
  }

  return {
    availabilityBackToAvailability,
    availabilityToAvailabilityBack,
    fetchUserPreferences,
  }
})
