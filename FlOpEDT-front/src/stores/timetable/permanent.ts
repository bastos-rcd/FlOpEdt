import { defineStore } from 'pinia'
import { Module, TimeSetting, TrainingProgramme } from '@/stores/declarations'
import { Ref, ref } from 'vue'
import { api } from '@/utils/api'
import { ModuleAPI, TrainingProgrammeAPI } from '@/ts/type'
import { useDepartmentStore } from '../department'
import { computed } from 'vue'

export const usePermanentStore = defineStore('permanent', () => {
  const trainProgs = ref<TrainingProgramme[]>([])
  const modules = ref<Module[]>([])
  const intervalMinutes = ref<number>(15)
  const isTrainProgsFetched = ref<boolean>(false)
  const isModulesFetched = ref<boolean>(false)
  const loadingError = ref<Error | null>(null)
  const departmentStore = useDepartmentStore()
  const timeSettings: Ref<Map<Number, TimeSetting>> = ref(new Map<Number, TimeSetting>())
  const areTimeSettingsFetched = ref<boolean>(false)
  const modulesSelected = ref<Module[]>([])
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

  async function fetchTimeSettings() {
    try {
      await api.getTimeSettings().then((result: TimeSetting[]) => {
        result.forEach((timeSetting: TimeSetting) => {
          timeSettings.value.set(timeSetting.departmentId, timeSetting)
        })
      })
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

  async function getModule(id: number): Promise<Module | undefined> {
    let module = modules.value.find((m) => m.id === id)
    if (!module && !isModulesFetched) {
      try {
        await fetchModules()
        module = modules.value.find((m) => m.id === id)
      } catch (error) {
        console.log('Get module failed')
        console.log(error)
      }
    }
    return module
  }

  async function getTrainProgs(id: number): Promise<TrainingProgramme | undefined> {
    let trainProg = trainProgs.value.find((tr) => tr.id === id)
    if (id) {
      if (!trainProg) {
        try {
          await fetchTrainingProgrammes()
          trainProg = trainProgs.value.find((tr) => tr.id === id)
        } catch (error) {
          console.log(`Get Training Program failed`)
          console.log(error)
        }
      }
    }
    return trainProg
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
    fetchTimeSettings,
    clearTrainProgs,
    clearModules,
    moduleColor,
    getModule,
    getTrainProgs,
    isModulesFetched,
    isTrainProgsFetched,
    areTimeSettingsFetched,
    timeSettings,
    intervalMinutes,
    modulesSelected,
  }
})
