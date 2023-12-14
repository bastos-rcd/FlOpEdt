import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Room } from '@/stores/declarations'
import { Department, RoomAPI } from '@/ts/type'
import { api } from '@/utils/api'

export const useRoomStore = defineStore('room', () => {
  const roomsFetched = ref<Array<Room>>([])
  const isLoading = ref<boolean>(false)
  const loadingError = ref<Error | null>(null)
  const getRoomById = computed(() => {
    return async (roomId: number) => {
      let room: Room | undefined = roomsFetched.value?.find((r) => r.id == roomId)
      if (!room) {
        try {
          await api.getRoomById(roomId).then((result) => {
            room = {
              id: result.id,
              abbrev: '',
              name: result.name,
              subroomIdOf: [],
              departmentIds: [],
            }
            roomsFetched.value.push(room)
          })
        } catch (e) {
          loadingError.value = e as Error
        }
      }
      return room
    }
  })

  async function fetchRooms(department?: Department): Promise<void> {
    isLoading.value = true
    try {
      await api.getAllRooms(department).then((result) => {
        result.forEach((r: RoomAPI) => {
          roomsFetched.value.push({
            id: r.id,
            abbrev: '',
            name: r.name,
            subroomIdOf: [],
            departmentIds: [],
          })
        })
        isLoading.value = false
      })
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  return { fetchRooms, roomsFetched, getRoomById }
})
