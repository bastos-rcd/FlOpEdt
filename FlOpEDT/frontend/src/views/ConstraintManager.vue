<template>
    <DisplayDocInPopoverAdapter :showDoc="showDoc" @updateShowDoc="swap"></DisplayDocInPopoverAdapter>
    <Suspense>
        <DisplayDocInNewConstraintAdapter :showDoc="showDoc" @updateShowDoc="swap"></DisplayDocInNewConstraintAdapter>
    </Suspense>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DisplayDocInPopoverAdapter from '@/components/adapter/DisplayDocInPopoverAdapter.vue'
import DisplayDocInNewConstraintAdapter from '@/components/adapter/DisplayDocInNewConstraintAdapter.vue'

/** =========================================================================================
 * Main component of the constraints page.
 * Load sub components and pilots the common showdoc var
 */

const showDoc = ref(false)

/**
 * this function change the value of the showDoc
 */
function swap() {
    showDoc.value = !showDoc.value
}
</script>
