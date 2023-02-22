<template>
    <div @click="clicked">
        <slot name="table"></slot>
    </div>
</template>

<script setup lang="ts">
import type { CalendarSlotInterface } from '@/assets/js/types'
import { ref } from 'vue'

const slotInterfaces = ref<{ [key: string]: CalendarSlotInterface }>({})

const currentContextMenu = ref<string>('')

function storeSlotInterface(id: string, slotInterface: CalendarSlotInterface) {
    slotInterfaces.value[id] = slotInterface
}

function openContextMenu(slotId: string) {
    closeCurrentContextMenu()

    // Store the current context menu if opened successfully
    if (slotInterfaces.value[slotId].openContextMenu()) {
        currentContextMenu.value = slotId
    }
}

function closeCurrentContextMenu() {
    // Close currently opened context menu (if exists)
    if (currentContextMenu.value) {
        slotInterfaces.value[currentContextMenu.value].closeContextMenu()
    }
}

function clicked() {
    closeCurrentContextMenu()
}

defineExpose({ openContextMenu, closeCurrentContextMenu, storeSlotInterface })
</script>

<script lang="ts">
export default {
    name: 'BaseCalendar',
    components: {},
}
</script>

<style>
.slot > div {
    height: 100%;
}
</style>
