<template>
    <div>
        <div class="input-group mb-3">
            <span class="input-group-text">Repeat each</span>
            <select
                v-model="selectedX"
                class="form-select"
                aria-label="Select occurrence number"
                :class="dayChoiceClass"
                :disabled="props.isDisabled"
            >
                <option :value="undefined" disabled>Select an occurrence number</option>
                <option v-for="x in byMonthXChoices" :key="x[0]" :value="x[0]">
                    {{ x[1] }}
                </option>
            </select>
            <select v-model="selectedDay" class="form-select" aria-label="Select a day" :disabled="props.isDisabled">
                <option value="" disabled>Select a day</option>
                <option v-for="day in props.weekdays" :key="day.num" :value="day.ref">
                    {{ day.name }}
                </option>
            </select>
            <span class="input-group-text">of each month</span>
        </div>
    </div>
</template>

<script setup lang="ts">
import { apiKey, requireInjection } from '@/assets/js/keys'
import { computed, onMounted, ref } from 'vue'
import type { ReservationPeriodicityByMonth, ReservationPeriodicityByMonthXChoice } from '@/assets/js/types'
import { WeekDay } from '@/assets/js/types'

interface Props {
    weekdays: Array<WeekDay>
    model: ReservationPeriodicityByMonth
    isDisabled: boolean
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:model', model: ReservationPeriodicityByMonth): void
}

const emit = defineEmits<Emits>()

const api = requireInjection(apiKey)

const byMonthXChoices = ref<Array<ReservationPeriodicityByMonthXChoice>>([])

const updatedModel = ref<ReservationPeriodicityByMonth>({
    id: props.model.id,
    start: props.model.start,
    end: props.model.end,
    periodicity_type: props.model.periodicity_type,
    bm_day_choice: props.model.bm_day_choice,
    bm_x_choice: props.model.bm_x_choice,
})

const selectedDay = computed({
    get() {
        return props.model.bm_day_choice
    },
    set(value) {
        updatedModel.value.bm_day_choice = value
        emitUpdate()
    },
})

const selectedX = computed({
    get() {
        return props.model.bm_x_choice
    },
    set(value) {
        updatedModel.value.bm_x_choice = value
        emitUpdate()
    },
})

function emitUpdate() {
    emit('update:model', updatedModel.value)
}

const dayChoiceClass = computed(() => (selectedDay.value ? '' : 'border border-danger'))

onMounted(() => {
    api.fetch.reservationPeriodicityByMonthXChoices().then((value) => (byMonthXChoices.value = value))
})
</script>

<script lang="ts">
export default {
    name: 'PeriodicityByMonthEdit',
    components: {},
}
</script>

<style scoped></style>
