import { api } from '@/composables/api'
import { defineStore } from 'pinia'
import { Department } from '@/ts/type'
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

export const useDepartmentStore = defineStore('dept', () => {
    const departments = ref<Array<Department>>([])
    const currentDepartment = ref(new Department())
  
    const getCurrentDepartment = computed(() => currentDepartment.value)

    const getAllDepartmentsFetched = computed(() => departments.value)

    const isCurrentDepartmentSelected = computed(() => currentDepartment.value.id !== -1)

    async function fetchAllDepartments() : Promise<void> {
      await api?.getAllDepartments().then((json: any) => {
        departments.value = json
      })
    }
  
    function setCurrentDepartment(dept : Department) : void {
        currentDepartment.value = dept
    }
  
    function cleanCurrentDepartment() : void {
      setCurrentDepartment(new Department())
    }

    async function getDepartmentFromURL() : Promise<void> {
      const route = useRoute()
      getAllDepartmentsFetched.value.forEach(dept => {
        const path = route.path.split("/")
        path.forEach(arg => {
          if(arg.includes(dept.abbrev)) {
            setCurrentDepartment(dept)
          }
        })
      })
    }
    
    return { 
      getCurrentDepartment,
      fetchAllDepartments,
      getAllDepartmentsFetched,
      setCurrentDepartment,
      isCurrentDepartmentSelected,
      cleanCurrentDepartment,
      getDepartmentFromURL,
    }
  })