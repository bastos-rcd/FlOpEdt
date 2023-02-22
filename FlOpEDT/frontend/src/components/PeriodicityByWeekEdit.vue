<template>
    <div>
        <div class="mb-2">
            <div :class="weekDaysClass">
                <div v-for="weekday in props.weekdays" :key="weekday.num" class="form-check form-check-inline">
                    <input
                        class="form-check-input"
                        type="checkbox"
                        :id="`checkbox-weekday-${weekday.num}`"
                        :value="weekday.ref"
                        v-model="selectedWeekDays"
                        :disabled="props.isDisabled"
                    />
                    <label class="form-check-label" :for="`checkbox-weekday-${weekday.num}`">{{ weekday.name }}</label>
                </div>
            </div>
            <span v-if="selectedWeekDays.length === 0" class="text-danger">* Required</span>
        </div>
        <div class="form-floating">
            <input
                type="number"
                class="form-control"
                id="input-weeks-interval"
                v-model="weekInterval"
                min="1"
                :disabled="props.isDisabled"
            />
            <label for="input-weeks-interval" class="form-label">Week interval</label>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { ReservationPeriodicityByWeek, WeekDay } from '@/assets/js/types'
import { computed, ref } from 'vue'

interface Props {
    weekdays: Array<WeekDay>
    model: ReservationPeriodicityByWeek
    isDisabled: boolean
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:model', model: ReservationPeriodicityByWeek): void
}

const emit = defineEmits<Emits>()

const updatedModel = ref<ReservationPeriodicityByWeek>({
    id: props.model.id,
    start: props.model.start,
    end: props.model.end,
    periodicity_type: props.model.periodicity_type,
    bw_weeks_interval: props.model.bw_weeks_interval,
    bw_weekdays: props.model.bw_weekdays,
})

const selectedWeekDays = computed({
    get() {
        return updatedModel.value.bw_weekdays
    },
    set(value) {
        updatedModel.value.bw_weekdays = value
        emitUpdate()
    },
})

const weekInterval = computed({
    get() {
        return updatedModel.value.bw_weeks_interval
    },
    set(value) {
        updatedModel.value.bw_weeks_interval = value
        emitUpdate()
    },
})

const weekDaysClass = computed(() => {
    return selectedWeekDays.value.length === 0 ? 'border border-danger rounded' : ''
})

function emitUpdate() {
    emit('update:model', updatedModel.value)
}
</script>

<script lang="ts">
export default {
    name: 'PeriodicityByWeekEdit',
    components: {},
}
</script>

<style scoped></style>
