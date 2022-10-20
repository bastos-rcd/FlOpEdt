<template>
    <div>
        <select
            v-model="selectedType"
            class="form-select mb-2"
            aria-label="Select periodicity type"
            :disabled="props.isDisabled"
        >
            <option :value="undefined" disabled>Select a periodicity type</option>
            <option v-for="type in props.types" :key="type[0]" :value="type">
                {{ type[1] }}
            </option>
        </select>
        <PeriodicityByWeekEdit
            v-if="selectedType && selectedType[0] === 'BW'"
            :weekdays="props.weekdays"
            :is-disabled="props.isDisabled"
            v-model:model="updatedModelByWeek"
        ></PeriodicityByWeekEdit>
        <PeriodicityByMonthEdit
            v-if="selectedType && selectedType[0] === 'BM'"
            :weekdays="props.weekdays"
            :is-disabled="props.isDisabled"
            v-model:model="updatedModelByMonth"
        ></PeriodicityByMonthEdit>
    </div>
</template>

<script setup lang="ts">
import type {
    ReservationPeriodicityByMonth,
    ReservationPeriodicityByWeek,
    ReservationPeriodicityData,
    ReservationPeriodicityType,
    ReservationPeriodicityTypeName,
    WeekDay,
} from '@/assets/js/types'
import { computed, ref, watch } from 'vue'
import PeriodicityByWeekEdit from '@/components/PeriodicityByWeekEdit.vue'
import PeriodicityByMonthEdit from '@/components/PeriodicityByMonthEdit.vue'

type PeriodicityModel = {
    [periodicityTypeName in ReservationPeriodicityTypeName]: ReservationPeriodicityData
}

interface Props {
    types: Array<ReservationPeriodicityType>
    weekdays: Array<WeekDay>
    modelType: ReservationPeriodicityType
    modelPeriodicity: PeriodicityModel
    isDisabled: boolean
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:modelPeriodicity', model: PeriodicityModel): void

    (e: 'update:modelType', model: ReservationPeriodicityType): void
}

const emit = defineEmits<Emits>()

const selectedType = computed({
    get() {
        return props.modelType
    },
    set(value) {
        emit('update:modelType', value)
    },
})

const updatedModel = ref(props.modelPeriodicity)

watch(
    () => props.modelPeriodicity,
    (newValue) => {
        Object.values(updatedModel.value).forEach((value) => {
            value.start = newValue.BW.start
            value.end = newValue.BW.end
        })
    }
)

const updatedModelByWeek = computed<ReservationPeriodicityByWeek>({
    get() {
        return updatedModel.value.BW as ReservationPeriodicityByWeek
    },
    set(value) {
        updatedModel.value.BW = value
        emit('update:modelPeriodicity', updatedModel.value)
    },
})

const updatedModelByMonth = computed<ReservationPeriodicityByMonth>({
    get() {
        return updatedModel.value.BM as ReservationPeriodicityByMonth
    },
    set(value) {
        updatedModel.value.BM = value
        emit('update:modelPeriodicity', updatedModel.value)
    },
})
</script>

<script lang="ts">
export default {
    name: 'PeriodicitySelect',
    components: {},
}
</script>

<style scoped></style>
