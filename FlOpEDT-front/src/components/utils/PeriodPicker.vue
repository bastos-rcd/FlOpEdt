<script setup lang="ts">
import { ToggleGroupItem, ToggleGroupRoot } from 'radix-vue'
import { computed } from 'vue'
const props = defineProps<{
  toggled: string[]
}>()
const emits = defineEmits<{
  (e: 'update:days', v: string[]): void
}>()

const toggledModel = computed({
  get() {
    return props.toggled
  },
  set(value: string[]) {
    emits('update:days', value)
  },
})
</script>

<template>
  <ToggleGroupRoot v-model="toggledModel" type="multiple" class="ToggleGroup">
    <ToggleGroupItem value="mo" class="ToggleGroupItem"><span>mo</span> </ToggleGroupItem>
    <ToggleGroupItem value="tu" class="ToggleGroupItem"><span>tu</span> </ToggleGroupItem>
    <ToggleGroupItem value="we" class="ToggleGroupItem"><span>we</span> </ToggleGroupItem>
    <ToggleGroupItem value="th" class="ToggleGroupItem"><span>th</span> </ToggleGroupItem>
    <ToggleGroupItem value="fr" class="ToggleGroupItem"><span>fr</span> </ToggleGroupItem>
    <ToggleGroupItem value="sa" class="ToggleGroupItem"><span>sa</span> </ToggleGroupItem>
    <ToggleGroupItem value="su" class="ToggleGroupItem"><span>su</span> </ToggleGroupItem>
  </ToggleGroupRoot>
</template>

<style scoped>
.ToggleGroup {
  display: inline-flex;
  background-color: mediumpurple;
  border-radius: 4px;
  box-shadow: 0 2px 10px black;
}

.ToggleGroupItem {
  background-color: white;
  color: purple;
  height: 35px;
  width: 35px;
  display: flex;
  font-size: 15px;
  line-height: 1;
  align-items: center;
  justify-content: center;
  margin-left: 1px;
}
.ToggleGroupItem:first-child {
  margin-left: 0;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}
.ToggleGroupItem:last-child {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}
.ToggleGroupItem:hover {
  background-color: rgb(255, 255, 220);
}
.ToggleGroupItem[data-state='on'] {
  background-color: rgb(235, 235, 200);
  color: rgb(120, 120, 50);
}
.ToggleGroupItem:focus {
  position: relative;
  box-shadow: 0 0 0 2px black;
}
</style>