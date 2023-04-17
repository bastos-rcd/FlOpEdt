import { getAllTrainProg } from '@/composables/API_TrainProg'
import type { TrainProg } from '@/models/TrainProg'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'

class TrainProgStore extends SimpleStoreMap<number, TrainProg> {
    gatherData() {
        return getAllTrainProg()
    }
}

export const useTrainProgStore = defineStore('trainProg', () => {
    /**
     * Sorted by classes then by objects
     */
    const store: SimpleStoreMap<number, TrainProg> = new TrainProgStore()

    const items = store.items
    function insertNew(item: TrainProg) {
        store.insertNew(item)
    }
        
    function initialize() {
        return store.initialize()
    }

    return { items , insertNew, initialize }
})
