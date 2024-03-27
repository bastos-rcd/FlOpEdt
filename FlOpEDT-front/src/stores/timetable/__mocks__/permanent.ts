import { defineStore } from 'pinia'
import { Module, TimeSetting, TrainingProgramme } from '@/stores/declarations'
import { Ref, ref } from 'vue'
import { api } from '@/utils/api'
import { ModuleAPI } from '@/ts/type'
import { computed } from 'vue'

export const usePermanentStore = defineStore('permanent', () => {
  const trainProgs = ref<TrainingProgramme[]>([])
  const modules = ref<Module[]>([])
  const intervalMinutes = ref<number>(15)
  const isTrainProgsFetched = ref<boolean>(false)
  const isModulesFetched = ref<boolean>(false)
  const loadingError = ref<Error | null>(null)
  const timeSettings: Ref<Map<number, TimeSetting>> = ref(new Map<number, TimeSetting>())
  const areTimeSettingsFetched = ref<boolean>(false)
  const modulesSelected = ref<Module[]>([])
  const moduleColor = computed(() => {
    const moduleColors: Map<number, string> = new Map<number, string>()
    modules.value.forEach((mod: Module) => {
      const colorValue =
        'rgb(' +
        Math.ceil(Math.random() * 155) +
        ',' +
        Math.ceil(Math.random() * 155) +
        ',' +
        Math.ceil(Math.random() * 155) +
        ')'
      moduleColors.set(mod.id, colorValue)
    })
    return moduleColors
  })

  function fetchTimeSettings() {
    timeSettings.value.set(-1, {
      id: 1,
      dayStartTime: 360, //6h
      dayEndTime: 1080, //18h
      morningEndTime: 500,
      afternoonStartTime: 600,
      days: [],
      departmentId: -1,
    })
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
            url: mod.url,
            trainProgId: mod.train_prog_id,
            trainingPeriodId: mod.training_period_id,
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
    if (!module && !isModulesFetched.value) {
      try {
        await fetchModules()
        module = modules.value.find((m) => m.id === id)
      } catch (error) {
        console.log(error)
      }
    }
    return module
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
    fetchModules,
    fetchTimeSettings,
    clearTrainProgs,
    clearModules,
    moduleColor,
    getModule,
    isModulesFetched,
    isTrainProgsFetched,
    areTimeSettingsFetched,
    timeSettings,
    intervalMinutes,
    modulesSelected,
  }
})
