<template>
    <CalendarScheduledCourseSlot :data="props.data">
        <template #text>
            <p class="col-xl-auto">{{ props.data.course.course.module.abbrev }}</p>
            <p class="col-xl-auto">{{ props.data.course.tutor }}</p>
            <p class="col-xl-auto ms-auto">{{ startHour }} - {{ endHour }}</p>
        </template>
    </CalendarScheduledCourseSlot>
</template>

<script setup lang="ts">
import CalendarScheduledCourseSlot from '@/components/calendar/CalendarScheduledCourseSlot.vue'
import type { CalendarScheduledCourseSlotData } from '@/ts/types'
import { onMounted, ref } from 'vue'

interface Props {
    data: CalendarScheduledCourseSlotData
}

const props = defineProps<Props>()
const startHour = ref("")
const endHour = ref("")

onMounted(() => {
    // TEMPORARY PATCH
    // WHY SOME DATE ARE NOT CORRECTLY FORMATTED ?
    if(typeof(props.data.course.start_time) === 'string') {
        startHour.value = props.data.course.start_time
        endHour.value = props.data.endTime
    }
    else {
        startHour.value = props.data.startTime.toLocaleTimeString("en-US")
        endHour.value = props.data.endTime.toLocaleTimeString("en-US")
    }
})
</script>

<script lang="ts">
export default {
    name: 'RoomCalendarScheduledCourseSlot',
    components: {},
}
</script>

<style scoped></style>
