import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { StoreAction } from '@/stores/store'

interface DepartmentAPI {
    id: number
    abbrev: string
}

export interface Department {
    id: number
    abbrev: string
}

function convertToApp(department: Partial<DepartmentAPI>): Department {
    return { id: department.id ?? -1, abbrev: department.abbrev ?? 'Unknown' }
}

function convertToAPI(department: Partial<Department>): DepartmentAPI {
    return { id: department.id ?? -1, abbrev: department.abbrev ?? 'Unknown' }
}

export const useDepartmentStore = defineStore('department', () => {
    const depts = ref<Array<Department>>([])

    // Read-only value of the list of departments
    const departments = computed(() => depts.value)
    // Generate the default API functions
    const remote: StoreAction<Department, DepartmentAPI> = new StoreAction<Department, DepartmentAPI>(
        'fetch/alldepts',
        convertToApp,
        convertToAPI,
        (value) => (depts.value = value)
    )
    return { departments, remote }
})
