import { getAllTutor } from '@/composables/API_Tutor'
import type { Tutor } from '@/models/Tutor'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'

class TutorStore extends SimpleStoreMap<number, Tutor> {
    gatherData() {      
        return getAllTutor()
    }
}

export const useTutorStore = defineStore('tutor', () => {
    /**
     * Sorted by classes then by objects
     */
    const store: SimpleStoreMap<number, Tutor> = new TutorStore()
    
    const items = store.items
    
    function insertNew(item: Tutor) {
        store.insertNew(item)
    }

    function initialize() {
        return store.initialize()
    }

    return { items, insertNew, initialize }
})
