<template>
    <CalendarScheduledCourseSlot :data="props.data">
        <template #text>
            <p class="col-xl-auto">{{ props.data.course.course.module.abbrev }}</p>
            <p class="col-xl-auto">{{ props.data.course.tutor }}</p>
            <p class="col-xl-auto ms-auto">{{ props.data.startTime.text }}-{{ props.data.endTime.text }}</p>
        </template>
    </CalendarScheduledCourseSlot>
</template>

<script setup lang="ts">
import CalendarScheduledCourseSlot from '@/components/CalendarScheduledCourseSlot.vue'
import type { CalendarScheduledCourseSlotData } from '@/assets/js/types'

interface Props {
    data: CalendarScheduledCourseSlotData
}

const props = defineProps<Props>()
</script>

<script lang="ts">
export default {
    name: 'RoomCalendarScheduledCourseSlot',
    components: {},
}
</script>

<style scoped></style>
