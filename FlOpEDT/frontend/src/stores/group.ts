import type { Group } from '@/models/Group'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'
import { getAllGroup } from '@/composables/API_Group'

class GroupStore extends SimpleStoreMap<number,Group> {
    gatherData() {
        return getAllGroup()
    }
}

export const useGroupStore = defineStore('group', () => {
    /**
     * Sorted by classes then by objects
     */
    const store: SimpleStoreMap<number,Group> = new GroupStore()

    const items = store.items

    function insertNew(item:Group){
        store.insertNew(item)
    }
        
    function initialize() {
        return store.initialize()
    }

    return { items , insertNew, initialize }
})
