import { defineStore } from 'pinia'
import { Module, TrainingProgramme } from '@/stores/declarations'
import { ref } from 'vue'
import { api } from '@/utils/api'
import { ModuleAPI, TrainingProgrammeAPI } from '@/ts/type'

export const usePermanentStore = defineStore('permanent', () => {
  const trainProgs = ref<TrainingProgramme[]>([])
  const modules = ref<Module[]>([])
  const isTrainProgsFetched = ref<boolean>(false)
  const isModulesFetched = ref<boolean>(false)
  const loadingError = ref<Error | null>(null)

  async function fetchTrainingProgrammes() {
    try {
      await api.getTrainProgs().then((result: TrainingProgrammeAPI[]) => {
        result.forEach((tp: any) => {
          trainProgs.value.push({
            id: tp.id,
            name: tp.name,
            abbrev: tp.abbrev,
            departmentId: -1, // Not in API call
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
            id: mod.id, // Not in API call
            name: mod.name,
            abbrev: mod.abbrev,
            headId: -1, // string in API call
            url: '',
            trainProgId: -1, // string in API call
            description: '', // not in API call
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
  }
})
