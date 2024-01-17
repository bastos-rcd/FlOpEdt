import { AvailabilityBack } from '@/ts/type'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Availability } from '../declarations'
import {
  Timestamp,
  copyTimestamp,
  nextDay,
  parseTime,
  updateFormatted,
  updateMinutes,
} from '@quasar/quasar-ui-qcalendar'
import { api } from '@/utils/api'
import { dateToTimestamp, getDateStringFromTimestamp, getDateTimeStringFromDate, timestampToDate } from '@/helpers'
import { InputCalendarEvent } from '@/components/calendar/declaration'
import _ from 'lodash'

export const useAvailabilityStore = defineStore('availabilityStore', () => {
  const availabilitiesBack = ref<Map<string, AvailabilityBack[]>>(new Map<string, AvailabilityBack[]>())
  const availabilities = ref<Map<string, Availability[]>>(new Map<string, Availability[]>())
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)

  async function fetchUserAvailabilitiesBack(userId: number, from: Date, to: Date): Promise<void> {
    clearAvailabilities()
    isLoading.value = true
    try {
      await api.getAvailabilities(userId, from, to).then((result: AvailabilityBack[]) => {
        result.forEach((avb) => {
          const dateString = getDateTimeStringFromDate(avb.start_time, false)
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
      _.remove(availabilitiesOnDate!, (av) => av.id === availabilityInStore.id)
    }
    availabilitiesOnDate!.push(newAvail)
    return availabilities.value.get(dateString)!
  }

  function removeAvailibility(id: number, date?: Timestamp): void {
    let availabilitiesOnDate: Availability[] | undefined
    if (date) {
      availabilitiesOnDate = availabilities.value.get(getDateStringFromTimestamp(date))
      _.remove(availabilitiesOnDate!, (av) => av.id === id)
    } else {
      availabilities.value.forEach((availsD, date) => {
        _.remove(availsD, (av) => av.id === id)
      })
    }
  }

  function getAvailability(id: number, date?: Timestamp, remove: boolean = false): Availability | undefined {
    let availabilityReturned: Availability | undefined
    if (date) {
      const dateString = getDateStringFromTimestamp(date)
      availabilityReturned = availabilities.value.get(dateString)?.find((c) => c.id === id)
      if (availabilityReturned && remove) _.remove(availabilities.value.get(dateString)!, (c) => c.id === id)
    } else {
      availabilities.value.forEach((availabilitiesD, date) => {
        const availability = availabilitiesD.find((c) => c.id === id)
        if (availability) {
          availabilityReturned = availability
          if (remove) _.remove(availabilitiesD, (c) => c.id === id)
        }
      })
    }
    return availabilityReturned
  }

  function clearAvailabilities() {
    availabilities.value = new Map<string, Availability[]>()
    availabilitiesBack.value = new Map<string, AvailabilityBack[]>()
  }

  function getAvailabilitiesFromDateToDate(from: Timestamp, to?: Timestamp): Availability[] {
    let availabilitiesReturned: Availability[] = []
    if (!to)
      availabilities.value.get(getDateStringFromTimestamp(from))?.forEach((c) => {
        availabilitiesReturned.push(c)
      })
    else {
      let currentDate = copyTimestamp(from)
      while (currentDate.weekday !== to.weekday) {
        availabilities.value.get(getDateStringFromTimestamp(currentDate))?.forEach((c) => {
          availabilitiesReturned.push(c)
        })
        currentDate = updateFormatted(nextDay(currentDate))
      }
    }
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
    getAvailabilitiesFromDateToDate,
  }
})
