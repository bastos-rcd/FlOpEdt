<template>
    <ModalDialog :is-open="props.isOpen">
        <template #title>Reservation deletion</template>
        <template #body>
            <span>
                You are about to remove a reservation related to a periodicity, would you want to remove only this
                reservation, all the related reservations or this one and all the next?
            </span>
        </template>
        <template #buttons>
            <button type="button" class="btn btn-secondary" @click.stop="cancel">Cancel</button>
            <button type="button" class="btn btn-primary" @click.stop="confirmCurrent" :disabled="isLocked">
                <span v-if="isCurrentSelected">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <span class="visually-hidden">Loading...</span>
                </span>
                <span v-else>Just this one</span>
            </button>
            <button type="button" class="btn btn-primary" @click.stop="confirmAll" :disabled="isLocked">
                <span v-if="isAllSelected">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <span class="visually-hidden">Loading...</span>
                </span>
                <span v-else>All</span>
            </button>
            <button type="button" class="btn btn-primary" @click.stop="confirmFuture" :disabled="isLocked">
                <span v-if="isFutureSelected">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <span class="visually-hidden">Loading...</span>
                </span>
                <span v-else>This one and all the next</span>
            </button>
        </template>
    </ModalDialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RoomReservation } from '@/assets/js/types'
import ModalDialog from '@/components/ModalDialog.vue'

interface Props {
    isOpen: boolean
    reservation: RoomReservation
    onCancel: () => void
    onConfirmCurrent: (reservation: RoomReservation) => void
    onConfirmAll: (reservation: RoomReservation) => void
    onConfirmFuture: (reservation: RoomReservation) => void
}

const props = defineProps<Props>()

const isMounted = ref(false)
const isLocked = computed(() => isCurrentSelected.value || isAllSelected.value || isFutureSelected.value)
const isCurrentSelected = ref(false)
const isAllSelected = ref(false)
const isFutureSelected = ref(false)

watch(
    () => props.isOpen,
    (_) => {
        isCurrentSelected.value = false
        isAllSelected.value = false
        isFutureSelected.value = false
    }
)

function cancel() {
    props.onCancel()
}

function confirmCurrent() {
    isCurrentSelected.value = true
    props.onConfirmCurrent(props.reservation)
}

function confirmAll() {
    isAllSelected.value = true
    props.onConfirmAll(props.reservation)
}

function confirmFuture() {
    isFutureSelected.value = true
    props.onConfirmFuture(props.reservation)
}

onMounted(() => {
    isMounted.value = true
})
</script>

<script lang="ts">
export default {
    name: 'DeletePeriodicReservationDialog',
    components: {},
}
</script>

<style scoped></style>
