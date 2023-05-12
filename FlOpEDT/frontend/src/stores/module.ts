import { getAllModule } from '@/composables/API_Module'
import type { Module } from '@/models/Module'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'


class WeekStore extends SimpleStoreMap<number,Module> {
    gatherData() {
        return getAllModule()
    }
}

export const useModuleStore = defineStore('module', () => {
    /**
     * Sorted by classes then by objects
     */
    const store: SimpleStoreMap<number,Module> = new WeekStore()

    const items = store.items

    function insertNew(item:Module){
        store.insertNew(item)
    }
        
    function initialize() {
        return store.initialize()
    }

    return { items , insertNew, initialize }
})
