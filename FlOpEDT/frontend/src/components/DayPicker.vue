<template>
    <Datepicker
        v-model="selectDate"
        :locale="locale"
        text-input
        format="dd/MM/yyyy"
        week-numbers
        :enable-time-picker="false"
        auto-apply
        show-now-button
        :now-button-label="nowLabel"
        :transitions="false"
        :min-date="props.minDate"
        :clearable="props.clearable"
    >
        <template #dp-input="{ value }">
            <slot name="input" :value="value"></slot>
        </template>
    </Datepicker>
</template>

<script setup lang="ts">
import { toStringAtLeastTwoDigits } from '@/helpers'
import Datepicker from '@vuepic/vue-datepicker'
import type { Ref } from 'vue'
import { computed, defineEmits, ref, watch } from 'vue'

interface Emits {
    (e: 'update:date', value: string): void

    (e: 'update:week', value: number): void

    (e: 'update:year', value: number): void

    (e: 'onReset'): void
}

const emit = defineEmits<Emits>()

interface Props {
    startDate: Date | string
    clearable?: boolean
    shouldReset: boolean
    minDate?: string | Date
}

const props = defineProps<Props>()

const selectDate: Ref<Date> = computed({
    get() {
        return new Date(props.startDate)
    },
    set(value) {
        const refDate = value
        if (!refDate) {
            return 1
        }
        const startDate = new Date(refDate.getFullYear(), 0, 1)
        const days = Math.floor((refDate.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000))

        const day = toStringAtLeastTwoDigits(refDate.getDate())
        const month = toStringAtLeastTwoDigits(refDate.getMonth() + 1)
        const year = refDate.getFullYear()

        // TODO: Value should be formatted with Moment.js according to the browser's locale
        emit('update:date', `${year}-${month}-${day}`)
        emit('update:week', Math.ceil(days / 7))
        emit('update:year', year)
    },
})

watch(
    () => props.shouldReset,
    (newValue) => {
        if (newValue) {
            selectDate.value = new Date(props.startDate)
            emit('onReset')
        }
    }
)

const locale = ref('fr')

const nowLabel = ref("Aujourd'hui")
</script>

<script lang="ts">
export default {
    name: 'DayPicker',
    components: {},
}
</script>

<style scoped></style>
