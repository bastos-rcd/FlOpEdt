<template>
    <div class="documentationContainer">
        <div class="buttonContainer">
            <button id="doc-show-btn" :class="showBtnClassDefiner()" @click="swap">
                {{ showDoc ? hideLabel : showLabel }}
            </button>
        </div>
        <template v-if="showDoc">
            <div class="scrollbar scrollbar-primary">
                <template v-if="constraint">
                    <DocumentationLoader :constraint="constraint" />
                </template>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import DocumentationLoader from '@/components/controler/DocumentationLoader.vue'
import type { Constraint } from '@/models/Constraint'
/** =========================================================================================
 *  Control if the documentation need to be loaded
 */

/**
 * Properties declaration interface of the component
 */
interface Props {
    /**
     * Reference to know if the documentation is shown
     */
    showDoc: boolean
    /**
     * Constraint
     */
    constraint: Constraint | null
    /**
     * Hidding button label
     */
    hideLabel: string
    /**
     * Showing button label
     */
    showLabel: string
}
const props = withDefaults(defineProps<Props>(), {})

/**
 * Events emits by the component
 */
const emit = defineEmits<{
    (e: 'updateShowDoc', value: boolean): void
}>()

/**
 * doc-show-btn class definer
 * permit to setup the display parameters
 */
const showBtnClassDefiner = () => {
    return props.showDoc ? ' minusButton ' : ' plusButton '
}

/**
 * Swap showDoc value
 */
function swap() {
    emit('updateShowDoc', props.showDoc)
}
</script>
