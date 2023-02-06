import { api } from '@/composables/api'
import { defineStore } from 'pinia'
import { Department } from '@/ts/type'
import { computed, ref } from 'vue'

export const useDepartmentStore = defineStore('dept', () => {
    const departments = ref<Array<Department>>([])
    const currentDepartment = ref(new Department())
  
    const getCurrentDepartment = computed(() => currentDepartment.value)

    const getAllDepartments = computed(() => departments.value)

    const isCurrentDepartmentSelected = computed(() => currentDepartment.value.id !== -1)

    function fetchAllDepartments() : void {
      api?.getAllDepartments().then((json: any) => departments.value = json)
    }
  
    function setCurrentDepartment(dept : Department) : void {
        currentDepartment.value = dept
    }
  
    return { getCurrentDepartment, fetchAllDepartments, getAllDepartments, setCurrentDepartment, isCurrentDepartmentSelected}

  })