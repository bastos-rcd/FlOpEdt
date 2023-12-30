import { AvailabilityBack } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Availability } from '../declarations'
import { Timestamp, copyTimestamp, parseTime, updateMinutes } from '@quasar/quasar-ui-qcalendar'
import { api } from '@/utils/api'
import { dateToTimestamp, timestampToDate } from '@/helpers'

export const useAvailabilityStore = defineStore('availabilityStore', () => {
  const availabilitiesBack = ref<AvailabilityBack[]>([])
  const availabilities = ref<Availability[]>([])
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchUserAvailabilitiesBack(userId: number, from: Date, to: Date): Promise<void> {
    isLoading.value = true
    try {
      await api.getAvailabilities(userId, from, to).then((result) => {
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
    let start: Timestamp = dateToTimestamp(availabilityBack.start_time)
    let newAvailability: Availability = {
      id: availabilityBack.id,
      type: availabilityBack.av_type,
      //@ts-expect-error
      duration: (availabilityBack.end_time - availabilityBack.start_time) / 1000 / 60,
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
      start_time: timestampToDate(availability.start),
      end_time: timestampToDate(updateMinutes(startCopy, availability.duration + parseTime(startCopy))),
      value: availability.value,
      av_type: availability.type,
      dataId: availability.dataId,
    }
    return newAvailabilityBack
  }

  return {
    availabilityBackToAvailability,
    availabilityToAvailabilityBack,
    fetchUserAvailabilitiesBack,
    availabilities,
  }
})
