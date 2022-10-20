<template>
    <CalendarRoomReservationSlot :data="props.data" :actions="props.actions">
        <template #text>
            <p class="col-xl-auto">{{ props.data.reservation.title }}</p>
            <p class="col-xl-auto">{{ responsible }}</p>
            <p class="col-xl-auto ms-auto">{{ props.data.startTime.text }}-{{ props.data.endTime.text }}</p>
        </template>
    </CalendarRoomReservationSlot>
</template>

<script setup lang="ts">
import CalendarRoomReservationSlot from '@/components/calendar/CalendarRoomReservationSlot.vue'
import type { CalendarRoomReservationSlotData, CalendarSlotActions } from '@/assets/js/types'
import { computed } from 'vue'

interface Props {
    data: CalendarRoomReservationSlotData
    actions: CalendarSlotActions
}

const props = defineProps<Props>()

const responsible = computed(() => {
    const user = props.data.users[props.data.reservation.responsible]
    return user?.username
})
</script>

<script lang="ts">
export default {
    name: 'RoomCalendarRoomReservationSlot',
    components: {},
}
</script>

<style scoped></style>
