import { defineStore } from 'pinia'
import { Module, TrainingProgramme } from '@/stores/declarations'
import { ref } from 'vue'
import { api } from '@/utils/api'
import { ModuleAPI, TrainingProgrammeAPI } from '@/ts/type'
import { useDepartmentStore } from '../department'
import { computed } from 'vue'

export const usePermanentStore = defineStore('permanent', () => {
  const trainProgs = ref<TrainingProgramme[]>([])
  const modules = ref<Module[]>([])
  const isTrainProgsFetched = ref<boolean>(false)
  const isModulesFetched = ref<boolean>(false)
  const loadingError = ref<Error | null>(null)
  const departmentStore = useDepartmentStore()
  const moduleColor = computed(() => {
    const moduleColors: Map<number, string> = new Map<number, string>()
    modules.value.forEach((mod: Module) => {
      const colorValue =
        'rgb(' +
        Math.ceil(Math.random() * 255) +
        ',' +
        Math.ceil(Math.random() * 255) +
        ',' +
        Math.ceil(Math.random() * 255) +
        ')'
      moduleColors.set(mod.id, colorValue)
    })
    return moduleColors
  })

  async function fetchTrainingProgrammes() {
    try {
      await api.getTrainProgs(departmentStore.current.abbrev).then((result: TrainingProgrammeAPI[]) => {
        result.forEach((tp: any) => {
          trainProgs.value.push({
            id: tp.id,
            name: tp.name,
            abbrev: tp.abbrev,
            departmentId: tp.department_id,
          })
        })
      })
      isTrainProgsFetched.value = true
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  async function fetchModules() {
    try {
      await api.getModules().then((result) => {
        result.forEach((mod: ModuleAPI) => {
          modules.value.push({
            id: mod.id,
            name: mod.name,
            abbrev: mod.abbrev,
            headId: mod.head_id,
            url: '',
            trainProgId: mod.train_prog_id,
            description: mod.description,
          })
        })
      })
      isModulesFetched.value = true
    } catch (e) {
      loadingError.value = e as Error
    }
  }

  function clearTrainProgs() {
    trainProgs.value = []
    isTrainProgsFetched.value = false
  }

  function clearModules() {
    modules.value = []
    isModulesFetched.value = false
  }

  return {
    trainProgs,
    modules,
    fetchTrainingProgrammes,
    fetchModules,
    clearTrainProgs,
    clearModules,
    moduleColor,
  }
})
