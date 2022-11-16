<template>
    <Datepicker v-model="time" time-picker :transitions="false" :clearable="false">
        <template #dp-input="{ value }">
            <slot name="input" :value="value"></slot>
        </template>
    </Datepicker>
</template>

<script setup lang="ts">
import Datepicker from '@vuepic/vue-datepicker'
import { computed, watch } from 'vue'

interface Props {
    hours: number
    minutes: number
    shouldReset: boolean
}

const props = defineProps<Props>()

interface Emits {
    (e: 'updateTime', time: { hours: number; minutes: number }): void

    (e: 'onReset'): void
}

const emit = defineEmits<Emits>()

const time = computed({
    get() {
        return { hours: props.hours, minutes: props.minutes }
    },
    set(value) {
        emit('updateTime', { hours: value.hours, minutes: value.minutes })
    },
})

watch(
    () => props.shouldReset,
    (newValue) => {
        if (newValue) {
            time.value = {
                hours: props.hours,
                minutes: props.minutes,
            }
            emit('onReset')
        }
    }
)
</script>

<script lang="ts">
export default {
    name: 'TimePicker',
    components: {},
}
</script>

<style scoped></style>
