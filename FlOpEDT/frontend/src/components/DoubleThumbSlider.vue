<template>
    <MultiRangeSlider
        ref="slider"
        base-class-name="multi-range-slider slider"
        :min="props.initialMin"
        :max="props.initialMax"
        :ruler="false"
        :label="false"
        :min-value="props.initialMin"
        :max-value="props.initialMax"
        @input="storeValues"
        @mouseup="updateValues"
        @mouseenter="onMouseEnter"
        @mouseleave="onMouseLeave"
    />
</template>

<script setup lang="ts">
import MultiRangeSlider from 'multi-range-slider-vue'
import { ref } from 'vue'

interface Props {
    initialMin: number
    initialMax: number
    min: number
    max: number
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:min', min: number): void

    (e: 'update:max', max: number): void
}

const emit = defineEmits<Emits>()

// The reference to the range slider.
const slider = ref()

/**
 * Stores the values from the range slider if the mouse is inside it, otherwise stops the drag.
 * @param e An object having two number properties: `minValue` and `maxValue`.
 */
function storeValues(e: { minValue: number; maxValue: number }) {
    if (!isEnabled.value) {
        // The mouse is out, so stop the drag
        slider.value.valueMin = props.min
        slider.value.valueMax = props.max
        return
    }
}

function updateValues() {
    emit('update:min', slider.value.valueMin)
    emit('update:max', slider.value.valueMax)
}

/**
 * Enables the range slider.
 */
function onMouseEnter() {
    enableDrag()
}

/**
 * Disables the range slider and updates the stored value.
 */
function onMouseLeave() {
    disableDrag()
    updateValues()
}

const isEnabled = ref(false)

/**
 * Enables the range slider.
 */
function enableDrag() {
    isEnabled.value = true
}

/**
 * Disables the range slider.
 */
function disableDrag() {
    isEnabled.value = false
}
</script>

<script lang="ts">
export default {
    name: 'DoubleThumbSlider',
    components: {},
}
</script>

<style>
.slider {
    box-shadow: none;
    border: 0;
}

.slider .bar {
    margin-top: 25px;
}

.slider .bar-inner {
    background-color: var(--bs-primary);
}

.slider .bar > [class^='bar-'] {
    box-shadow: inset 0 0 1px black;
}

.slider .caption {
    display: block;
}

.slider .caption * {
    translate: -50% -50%;
    box-shadow: none !important;
}

.slider .thumb::before {
    box-shadow: none;
}
</style>
