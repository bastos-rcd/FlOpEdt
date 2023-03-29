<template>
    <div class="row">
        <Datepicker
            v-model="selectDate"
            :locale="locale"
            inline
            week-numbers
            week-picker
            :enable-time-picker="false"
            auto-apply
            show-now-button
            :now-button-label="nowLabel"
        />
    </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue'
import { defineEmits, ref, watchEffect } from 'vue'
import Datepicker from '@vuepic/vue-datepicker'

interface Props {
    week: number
    year: number
}

defineProps<Props>()

interface Emits {
    (e: 'update:week', value: number): void

    (e: 'update:year', value: number): void
}

const emits = defineEmits<Emits>()

const selectDate: Ref<Array<Date>> = ref([])

watchEffect(() => {
    const refDate = selectDate.value[0]
    if (!refDate) {
        return
    }
    emits('update:week', getNumberOfTheWeek(refDate))

    emits('update:year', refDate.getFullYear())
})

function getNumberOfTheWeek(date: Date) {
    // We get the first day of the year
    const yearStart = new Date(Date.UTC(date.getFullYear(), 0, 1))
    // We get the thursday of our week
    const currentThursday = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
    currentThursday.setUTCDate(currentThursday.getUTCDate() + 4 - (currentThursday.getUTCDay() || 7))
    return Math.ceil(((currentThursday.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
}

const locale = ref('fr')

const nowLabel = ref("Aujourd'hui")
</script>

<script lang="ts">
export default {
    name: 'WeekPicker',
    components: {},
}
</script>

<style scoped></style>
