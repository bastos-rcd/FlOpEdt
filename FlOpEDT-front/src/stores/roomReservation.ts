import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { FlopWeek, RoomReservation } from '@/ts/type'

export const useRoomReservationStore = defineStore('roomreservation', () => {
  const roomReservations = ref<any>([])

  const getRoomReservationById = computed((id: number) =>
    roomReservations.value.find((rResa: RoomReservation) => rResa.id === id)
  )

  const getAllRoomReservationsFetched = computed(() => roomReservations.value)

  /*
   * This method delete all data formerly fetched in this
   * store.
   **/
  async function fetchRoomReservationsForWeek(week: FlopWeek): Promise<void> {
    await api.fetch.roomReservations({ week: week.week, year: week.year }).then((value: RoomReservation[]) => {
      if (value !== undefined) roomReservations.value = value
    })
  }

  return {
    fetchRoomReservationsForWeek,
    getRoomReservationById,
    getAllRoomReservationsFetched,
  }
})
