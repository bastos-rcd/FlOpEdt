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
            :now-button-label="`${ $t('roomreservation.weekpicker.today-button') }`"
        />
    </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue'
import { ref, watchEffect } from 'vue'
import Datepicker from '@vuepic/vue-datepicker'
import { useI18n } from 'vue-i18n';

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
    const startDate = new Date(refDate.getFullYear(), 0, 1)
    const days = Math.floor((refDate.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000))

    emits('update:week', Math.ceil(days / 7))
    emits('update:year', refDate.getFullYear())
})

const { t, locale } = useI18n()

</script>

<script lang="ts">
export default {
    name: 'WeekPicker',
    components: {},
}
</script>

<style scoped></style>
