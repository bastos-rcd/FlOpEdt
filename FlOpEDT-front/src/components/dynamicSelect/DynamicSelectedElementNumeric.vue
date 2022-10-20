<template>
    <DynamicSelectedElement :value="props.value">
        <template #input>
            <DoubleThumbSlider
                :initial-min="props.value.initialMin"
                :initial-max="props.value.initialMax"
                v-model:min="minValue"
                v-model:max="maxValue"
            ></DoubleThumbSlider>
        </template>
    </DynamicSelectedElement>
</template>

<script setup lang="ts">
import DynamicSelectedElement from '@/components/dynamicSelect/DynamicSelectedElement.vue'
import { ref, watch } from 'vue'
import type { DynamicSelectElementNumericValue } from '@/assets/js/types'
import DoubleThumbSlider from '@/components/DoubleThumbSlider.vue'

interface Props {
    value: DynamicSelectElementNumericValue
}

const props = defineProps<Props>()

interface Emits {
    /**
     * Calls the update of the `value` model.
     * @param e The event that triggers the model change.
     * @param value The new value of the model.
     */
    (e: 'update:value', value: DynamicSelectElementNumericValue): void
}

const emit = defineEmits<Emits>()

// The value used to update the model.
const inputValues = ref(props.value)

// The min value from the range slider
const minValue = ref(inputValues.value.min)

// The max value from the range slider
const maxValue = ref(inputValues.value.max)

watch(minValue, (newMin) => {
    inputValues.value.min = newMin
    emit('update:value', inputValues.value)
})

watch(maxValue, (newMax) => {
    inputValues.value.max = newMax
    emit('update:value', inputValues.value)
})
</script>

<script lang="ts">
export default {
    name: 'DynamicSelectedElementNumeric',
    components: {},
}
</script>

<style scoped></style>
