import { api } from '@/composables/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { FlopWeek, RoomReservation } from '@/ts/type'

export const useRoomReservationStore = defineStore('roomreservation', () => {
    const roomReservations = ref<Array<RoomReservation>>([])
  
    const getRoomReservationById = computed((id: number) => roomReservations.value.find(rResa => rResa.id===id))

    const getAllRoomReservationsFetched = computed(() => roomReservations.value)

    /*
     * This method delete all data formerly fetched in this
     * store.
     **/
    async function fetchRoomReservationsForWeek(week: FlopWeek) : Promise<void> {
        api.fetch.roomReservations({ week: week.week, year: week.year }).then((value: RoomReservation[]) => {
            roomReservations.value = value
        })
    }
    
    return {
        fetchRoomReservationsForWeek,
        getRoomReservationById,
        getAllRoomReservationsFetched
    }
  })