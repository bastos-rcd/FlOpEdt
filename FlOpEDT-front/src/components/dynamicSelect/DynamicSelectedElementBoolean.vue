<template>
    <DynamicSelectedElement :value="props.value">
        <template #input>
            <div>
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" role="switch" v-model="updatedValue" />
                </div>
            </div>
        </template>
    </DynamicSelectedElement>
</template>

<script setup lang="ts">
import DynamicSelectedElement from '@/components/dynamicSelect/DynamicSelectedElement.vue'
import type { DynamicSelectElementBooleanValue } from '@/assets/js/types'
import { computed, ref } from 'vue'

interface Props {
    value: DynamicSelectElementBooleanValue
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:value', value: DynamicSelectElementBooleanValue): void
}

const emit = defineEmits<Emits>()

const elementValue = ref(props.value)

const updatedValue = computed({
    get() {
        return elementValue.value.value
    },
    set(value) {
        elementValue.value.value = value
    },
})
emit('update:value', elementValue.value)
</script>

<script lang="ts">
export default {
    name: 'DynamicSelectedElementBoolean',
    components: {},
}
</script>

<style scoped></style>
