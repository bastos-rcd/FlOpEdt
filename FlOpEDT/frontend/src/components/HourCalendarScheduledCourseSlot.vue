<template>
    <CalendarScheduledCourseSlot :data="props.data">
        <template #text>
            <p class="col-xl-6">{{ props.data.course.course.module.abbrev }}</p>
            <p class="col-xl-6">{{ props.data.department }}</p>
            <p class="col-xl-6">{{ props.data.course.tutor }}</p>
            <p class="col-xl-6">{{ roomName }}</p>
        </template>
    </CalendarScheduledCourseSlot>
</template>

<script setup lang="ts">
import CalendarScheduledCourseSlot from '@/components/CalendarScheduledCourseSlot.vue'
import { computed } from 'vue'
import type { CalendarScheduledCourseSlotData } from '@/assets/js/types'
import type { Room } from '@/stores/room'

interface Props {
    data: CalendarScheduledCourseSlotData
}

const props = defineProps<Props>()

const roomName = computed(() => {
    let r: Room
    if (props.data.course.room) {
        r = props.data.rooms[props.data.course.room.id]
        return r.name
    }
    return 'UNKNOWN'
})
</script>

<script lang="ts">
export default {
    name: 'HourCalendarScheduledCourseSlot',
    components: {},
}
</script>

<style scoped></style>
