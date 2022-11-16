<template>
    <div class="row">
        <label :for="props.inputId" class="form-label">{{ props.label }}</label>
        <div v-if="props.text.length > 0" class="col-auto pe-0">
            <button type="button" class="btn-close" @click="clear()"></button>
        </div>
        <div class="col-auto">
            <input :id="props.inputId" type="text" class="form-control" v-model="model" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    inputId: string
    label: string
    text: string
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:text', newText: string): void
}

const emit = defineEmits<Emits>()

const model = computed({
    get() {
        return props.text
    },
    set(value) {
        emit('update:text', value)
    },
})

function clear() {
    model.value = ''
}
</script>

<script lang="ts">
export default {
    name: 'ClearableInput',
    components: {},
}
</script>

<style scoped></style>
