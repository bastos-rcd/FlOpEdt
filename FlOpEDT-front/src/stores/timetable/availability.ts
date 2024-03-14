import { AvailabilityBack } from '@/ts/type'
import { defineStore } from 'pinia'
import { Ref, ref } from 'vue'
import { Availability } from '../declarations'
import { Timestamp, copyTimestamp } from '@quasar/quasar-ui-qcalendar'
import { api } from '@/utils/api'
import {
  dateToTimestamp,
  getDateStringFromTimestamp,
  timestampToDate,
  datetimeStringToDate,
  durationDjangoToMinutes,
  durationMinutesToDjango,
} from '@/helpers'
import { InputCalendarEvent } from '@/components/calendar/declaration'
import { remove } from 'lodash'

export const useAvailabilityStore = defineStore('availabilityStore', () => {
  const availabilitiesBack = ref<Map<string, AvailabilityBack[]>>(new Map<string, AvailabilityBack[]>())
  const availabilities = ref<Map<string, Availability[]>>(new Map<string, Availability[]>())
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)
  const nextId: Ref<number> = ref(0)

  async function fetchUserAvailabilitiesBack(userId: number, from: Date, to: Date): Promise<void> {
    clearAvailabilities()
    isLoading.value = true
    try {
      await api.getAvailabilities(userId, from, to).then((result: AvailabilityBack[]) => {
        result.forEach((avb) => {
          const dateString = datetimeStringToDate(avb.start_time)
          if (!availabilitiesBack.value.has(dateString)) {
            availabilitiesBack.value.set(dateString, [])
          }
          availabilitiesBack.value.get(dateString)!.push(avb)
          if (!availabilities.value.has(dateString)) {
            availabilities.value.set(dateString, [])
          }
          availabilities.value.get(dateString)!.push(availabilityBackToAvailability(avb))
        })
        isLoading.value = false
      })
    } catch (e) {
      loadingError.value = e as Error
      isLoading.value = false
    }
  }

  function availabilityBackToAvailability(availabilityBack: AvailabilityBack): Availability {
    let start: Timestamp = dateToTimestamp(new Date(availabilityBack.start_time))
    let newAvailability: Availability = {
      id: nextId.value++,
      type: availabilityBack.av_type,
      duration: durationDjangoToMinutes(availabilityBack.duration),
      start: start,
      value: availabilityBack.value,
      dataId: availabilityBack.dataId,
    }
    return newAvailability
  }

  function availabilityToAvailabilityBack(availability: Availability): AvailabilityBack {
    let newAvailabilityBack: AvailabilityBack = {
      start_time: timestampToDate(availability.start).toISOString(),
      duration: durationMinutesToDjango(availability.duration),
      value: availability.value,
      av_type: availability.type,
      dataId: availability.dataId,
    }
    return newAvailabilityBack
  }

  function addOrUpdateAvailibility(
    availEvent: InputCalendarEvent,
    dataId?: number,
    availType?: string
  ): Availability[] {
    const dateString = getDateStringFromTimestamp(availEvent.data.start)
    if (!availabilities.value.has(dateString)) availabilities.value.set(dateString, [])
    const newAvail: Availability = {
      id: availEvent.id,
      duration: availEvent.data.duration!,
      start: copyTimestamp(availEvent.data.start),
      value: availEvent.data.value!,
      type: availType ? availType : 'user',
      dataId: dataId ? dataId : availEvent.data.dataId,
    }
    const availabilitiesOnDate = availabilities.value.get(dateString)
    const availabilityInStore = availabilitiesOnDate!.find((av) => av.id === availEvent.id)

    if (availabilityInStore) {
      newAvail.type = availabilityInStore.type
      newAvail.dataId = availabilityInStore.dataId
      remove(availabilitiesOnDate!, (av) => av.id === availabilityInStore.id)
    }
    availabilitiesOnDate!.push(newAvail)
    return availabilities.value.get(dateString)!
  }

  function removeAvailibility(id: number, date?: Timestamp): void {
    let availabilitiesOnDate: Availability[] | undefined
    if (date) {
      availabilitiesOnDate = availabilities.value.get(getDateStringFromTimestamp(date))
      remove(availabilitiesOnDate!, (av) => av.id === id)
    } else {
      availabilities.value.forEach((availsD, date) => {
        remove(availsD, (av) => av.id === id)
      })
    }
  }

  function getAvailability(id: number, date?: Timestamp, removed: boolean = false): Availability | undefined {
    let availabilityReturned: Availability | undefined
    if (date) {
      const dateString = getDateStringFromTimestamp(date)
      availabilityReturned = availabilities.value.get(dateString)?.find((c) => c.id === id)
      if (availabilityReturned && removed) remove(availabilities.value.get(dateString)!, (c: any) => c.id === id)
    } else {
      availabilities.value.forEach((availabilitiesD, date) => {
        const availability = availabilitiesD.find((c) => c.id === id)
        if (availability) {
          availabilityReturned = availability
          if (removed) remove(availabilitiesD, (c: any) => c.id === id)
        }
      })
    }
    return availabilityReturned
  }

  function clearAvailabilities() {
    availabilities.value = new Map<string, Availability[]>()
    availabilitiesBack.value = new Map<string, AvailabilityBack[]>()
  }

  function getAvailabilityFromDates(dates: Timestamp[]): Availability[] {
    const availabilitiesReturned: Availability[] = []
    dates.forEach((date) => {
      const dateString = getDateStringFromTimestamp(date)
      availabilities.value.get(dateString)?.forEach((av) => {
        availabilitiesReturned.push(av)
      })
    })
    return availabilitiesReturned
  }

  return {
    availabilityBackToAvailability,
    availabilityToAvailabilityBack,
    fetchUserAvailabilitiesBack,
    availabilities,
    addOrUpdateAvailibility,
    removeAvailibility,
    getAvailability,
    getAvailabilityFromDates,
  }
})
