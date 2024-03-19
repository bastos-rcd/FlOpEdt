import { AvailabilityBack } from '@/ts/type'
import { defineStore, storeToRefs } from 'pinia'
import { Ref, ref } from 'vue'
import { Availability } from '../declarations'
import { Timestamp, copyTimestamp, parseTime, parseTimestamp, updateMinutes } from '@quasar/quasar-ui-qcalendar'
import { api } from '@/utils/api'
import {
  getDateStringFromTimestamp,
  datetimeStringToDate,
  durationDjangoToMinutes,
  durationMinutesToDjango,
} from '@/helpers'
import { InputCalendarEvent } from '@/components/calendar/declaration'
import { cloneDeep, remove } from 'lodash'
import { usePermanentStore } from './permanent'
import { useDepartmentStore } from '../department'

export const useAvailabilityStore = defineStore('availabilityStore', () => {
  const permanentStore = usePermanentStore()
  const departmentStore = useDepartmentStore()
  const availabilitiesBack = ref<Map<string, AvailabilityBack[]>>(new Map<string, AvailabilityBack[]>())
  const availabilities = ref<Map<string, Availability[]>>(new Map<string, Availability[]>())
  const isLoading = ref(false)
  const loadingError = ref<Error | null>(null)
  const nextId: Ref<number> = ref(0)
  const { current } = storeToRefs(departmentStore)
  const { timeSettings } = storeToRefs(permanentStore)

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
          const newAvailabilities: Availability[] = formatAvailabilityWithDayTime(availabilityBackToAvailability(avb))
          newAvailabilities.forEach((newAvailability) => {
            if (!availabilities.value.has(dateString)) {
              availabilities.value.set(dateString, [])
            }
            availabilities.value.get(dateString)!.push(newAvailability)
          })
        })
        isLoading.value = false
      })
    } catch (e) {
      loadingError.value = e as Error
      isLoading.value = false
    }
  }

  function availabilityBackToAvailability(availabilityBack: AvailabilityBack): Availability {
    let start: Timestamp = parseTimestamp(availabilityBack.start_time) as Timestamp
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
      start_time: availability.start.date + ' ' + availability.start.time,
      duration: durationMinutesToDjango(availability.duration),
      value: availability.value,
      av_type: availability.type,
      dataId: availability.dataId,
    }
    return newAvailabilityBack
  }

  function createAvailability(avail: InputCalendarEvent): Availability[] {
    const newAvail: Availability = {
      id: nextId.value++,
      duration: avail.data.duration!,
      start: avail.data.start,
      value: avail.data.value!,
      type: 'avail',
      dataId: avail.data.dataId,
    }
    return addOrUpdateAvailibility(newAvail)
  }

  function addOrUpdateAvailibility(avail: Availability): Availability[] {
    const dateString = getDateStringFromTimestamp(avail.start)
    if (!availabilities.value.has(dateString)) availabilities.value.set(dateString, [])
    const availabilitiesOutput = availabilities.value.get(dateString)
    remove(availabilitiesOutput!, (av) => av.id === avail.id)
    availabilitiesOutput!.push(avail)
    return availabilitiesOutput!
  }

  function addOrUpdateAvailibilityEvent(
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
      if (availabilitiesOnDate) remove(availabilitiesOnDate, (av) => av.id === id)
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

  function formatAvailabilityWithDayTime(avail: Availability): Availability[] {
    let timeStart = parseTime(avail.start)
    const dayStartTime = timeSettings.value.get(current.value.id)!.dayStartTime
    const dayEndTime = timeSettings.value.get(current.value.id)!.dayEndTime
    const newAvail = cloneDeep(avail)
    const availabilitiesReturned = []
    if (timeStart < dayStartTime && timeStart + newAvail.duration > dayStartTime) {
      newAvail.start = updateMinutes(newAvail.start, dayStartTime)
      newAvail.id = nextId.value++
      avail.duration = dayStartTime - timeStart
      newAvail.duration = newAvail.duration - avail.duration
      availabilitiesReturned.push(newAvail, avail)
    }
    timeStart = parseTime(newAvail.start)
    if (timeStart < dayEndTime && timeStart + newAvail.duration > dayEndTime) {
      const newAvailUp = cloneDeep(newAvail)
      newAvailUp.start = updateMinutes(newAvailUp.start, dayEndTime)
      newAvailUp.id = nextId.value++
      newAvail.duration = dayEndTime - timeStart
      newAvailUp.duration = newAvailUp.duration - newAvail.duration
      if (newAvail.id !== avail.id) availabilitiesReturned.push(newAvail)
      availabilitiesReturned.push(newAvailUp)
    }
    return availabilitiesReturned
  }

  return {
    availabilityBackToAvailability,
    availabilityToAvailabilityBack,
    fetchUserAvailabilitiesBack,
    availabilities,
    addOrUpdateAvailibilityEvent,
    removeAvailibility,
    getAvailability,
    getAvailabilityFromDates,
    addOrUpdateAvailibility,
    createAvailability,
  }
})
