
import { getAllDepartement } from '@/composables/API_Departement'
import type { Department } from '@/models/Department'
import { defineStore } from 'pinia'
import { SimpleStoreMap } from './SimpleStoreMap'

class DepartmentStore extends SimpleStoreMap<number, Department> {
    gatherData() {
        return getAllDepartement()
    }
}

export const useDepartmentStore = defineStore('departmentRework', () => {
    /**
     * Sorted by classes then by objects
     */
    const store: SimpleStoreMap<number, Department> = new DepartmentStore()
    
    const items = store.items

    function insertNew(item: Department) {
        store.insertNew(item)
    }

    function initialize() {
        return store.initialize()
    }

    return { items, insertNew, initialize }
})
