<template>
  <div class="side-panel">
    <label>
      <CheckboxRoot @update:checked="handleCheckboxClick" class="CheckboxRoot">
        <CheckboxIndicator class="CheckboxIndicator">
          <icon icon="iconoir:check"></icon>
        </CheckboxIndicator>
      </CheckboxRoot>
      Show Availabilities ?
    </label>
  </div>
</template>
<script setup lang="ts">
import { CheckboxIndicator, CheckboxRoot } from 'radix-vue'
import { Icon } from '@iconify/vue'
const emits = defineEmits<{
  (e: 'update:checkbox', v: boolean): void
}>()
function handleCheckboxClick(v: boolean) {
  emits('update:checkbox', v)
}
</script>
<style>
.side-panel {
  top: 50px;
  padding-top: 10px;
  max-width: 150px;
  color: white;
  background-color: black;
  z-index: 5;
}
.CheckboxRoot {
  min-width: 57px;
  min-height: 57px;
}
</style>
