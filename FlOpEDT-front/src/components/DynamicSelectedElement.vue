<template>
    <div class="row">
        <button type="button" class="btn-close col-auto" aria-label="Close" @click="remove"></button>
        <div class="col">{{ props.value.name }}</div>
        <slot name="input"></slot>
    </div>
</template>

<script setup lang="ts">
import type { DynamicSelectElementValue } from '@/assets/js/types'

interface Props {
    value: DynamicSelectElementValue
}

const props = defineProps<Props>()

interface Emits {
    (e: 'removed', id: number): void
}

const emit = defineEmits<Emits>()

function remove() {
    emit('removed', props.value.id)
}
</script>

<script lang="ts">
export default {
    name: 'DynamicSelectedElement',
    components: {},
}
</script>

<style scoped></style>
