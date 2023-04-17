import { getAllRoom } from '@/composables/API_Room'
import type { Room } from '@/models/Room'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'

class RoomStore extends SimpleStoreMap<number,Room> {
    gatherData() {
        return getAllRoom()
    }
}

export const useRoomStore = defineStore('roomRework', () => {
    /**
     * Sorted by classes then by objects
     */
    const store: SimpleStoreMap<number,Room> = new RoomStore()

    const items = store.items
    function insertNew(item:Room){
        store.insertNew(item)
    }
        
    function initialize() {
        return store.initialize()
    }

    return { items , insertNew, initialize }
})
