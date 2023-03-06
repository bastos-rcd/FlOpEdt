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

    function getDepartmentFromURL(pathTo?: string) : void {
      const route = useRoute()
      let path : string[] = []
      if(pathTo !== undefined) {
        path = pathTo.split("/")
      } else {
        path = route.path.split("/")
      }
      getAllDepartmentsFetched.value.forEach(dept => {
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