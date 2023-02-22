<template>
    <Datepicker
        v-model="time"
        time-picker
        :transitions="false"
        :clearable="false"
        hours-increment="-1"
        minutes-increment="-1"
    >
        <template #dp-input="{ value }">
            <slot name="input" :value="value"></slot>
        </template>
    </Datepicker>
</template>

<script setup lang="ts">
import Datepicker from '@vuepic/vue-datepicker'
import { ref, watch, watchEffect } from 'vue'

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

const time = ref({
    hours: props.hours,
    minutes: props.minutes,
})

watchEffect(() => {
    emit('updateTime', { hours: time.value.hours, minutes: time.value.minutes })
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
