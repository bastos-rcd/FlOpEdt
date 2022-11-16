<template>
    <CalendarRoomReservationSlot :data="props.data" :actions="props.actions">
        <template #text>
            <p class="col-xl-6">{{ props.data.title }}</p>
            <p class="col-xl-6">{{ props.data.reservation.description }}</p>
            <p class="col-xl-6">{{ responsible }}</p>
            <p class="col-xl-6">{{ roomName }}</p>
        </template>
    </CalendarRoomReservationSlot>
</template>

<script setup lang="ts">
import CalendarRoomReservationSlot from '@/components/CalendarRoomReservationSlot.vue'
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
const roomName = computed(() => {
    const r = props.data.rooms[props.data.reservation.room]
    return r?.name
})
</script>

<script lang="ts">
export default {
    name: 'HourCalendarRoomReservationSlot',
    components: {},
}
</script>

<style scoped></style>
