import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { Department, StartTime } from '@/ts/type'
import { Ref, computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

export const useDepartmentStore = defineStore('dept', () => {
  const all = ref<Array<Department>>([])
  const current = ref(new Department())
  const isAllDepartmentsFetched = ref<boolean>(false)
  const isCurrentDepartmentSelected = computed(() => current.value.id !== -1)
  const startTimes: Ref<StartTime[]> = ref([])

  watch(current, async () => {
    await api.getStartTimes(current.value.id).then((result: StartTime[]) => {
      startTimes.value = result
    })
  })

  async function fetchAllDepartments(): Promise<void> {
    await api.getAllDepartments().then((json: Department[]) => {
      all.value = json
    })
    isAllDepartmentsFetched.value = true
  }

  function cleanCurrentDepartment(): void {
    current.value = new Department()
  }

  function getDepartmentFromURL(pathTo?: string): void {
    const route = useRoute()
    let path: string[] = []
    if (pathTo !== undefined) {
      path = pathTo.split('/')
    } else {
      path = route.path.split('/')
    }
    all.value.forEach((dept) => {
      path.forEach((pathOpt) => {
        if (pathOpt.includes(dept.abbrev)) {
          current.value = dept
        }
      })
    })
  }

  return {
    current,
    fetchAllDepartments,
    all,
    isCurrentDepartmentSelected,
    isAllDepartmentsFetched,
    cleanCurrentDepartment,
    getDepartmentFromURL,
    startTimes,
  }
})
