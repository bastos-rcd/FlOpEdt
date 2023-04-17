import { getAllWeek } from '@/composables/API_Week'
import type { Week } from '@/models/Week'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'

class WeekStore extends SimpleStoreMap<number,Week> {
    gatherData() {
        return getAllWeek()
    }
}

export const useWeekStore = defineStore('week', () => {
    /**
     * Sorted by classes then by objects
     */
    const store: SimpleStoreMap<number,Week> = new WeekStore()

    const items = store.items
    function insertNew(item:Week){
        store.insertNew(item)
    }
        
    function initialize() {
        return store.initialize()
    }

    return { items , insertNew, initialize }
})
