<template>
  <button class="cancel-button" @click="onClick">
    <div><Icon icon="iconoir:cancel" width="24" height="24" /></div>
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
  max-width: 25px;
  max-height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 5px 5px 5px;
  margin: 5px 10px;
  border-radius: 50%;
}
.cancel-button div {
  display: flex;
}
.cancel-button:hover {
  background-color: #fff;
}
</style>
