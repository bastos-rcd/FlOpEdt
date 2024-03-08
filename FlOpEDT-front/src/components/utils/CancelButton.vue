<template>
  <button class="cancel-button" @click="onClick">
    <span><Icon icon="iconoir:cancel" width="24" height="24" /></span>
  </button>
</template>
<script setup lang="ts">
import { Icon } from '@iconify/vue'
const emits = defineEmits<{
  (e: 'cancelClick'): void
}>()
function onClick() {
  emits('cancelClick')
}
</script>

<style>
.cancel-button {
  background-color: #bbb;
  max-width: 15px;
  max-height: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 10px 8px 10px;
  margin: 5px 10px;
}
.cancel-button:hover {
  background-color: #fff;
}
</style>
