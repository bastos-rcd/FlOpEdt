<template>
  <q-select
    clearable
    id="select-item"
    v-model="selectionModel"
    :options="props.items"
    :option-label="props.itemVariableName"
    class="form-select w-auto"
    :label="filterSelectorUndefinedLabel"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

/*
 *  items : list of objects we can chose in the selector
 *  filterSelectorUndefinedLabel : text label displayed above the selector box & default text label inside selector box
 *  selectedItem : The current selectedItem =
 *  itemVariableName: attribute name of the objects.
 **/
interface Props {
  items: any[]
  filterSelectorUndefinedLabel: string
  selectedItem: any
  itemVariableName: string
}

const emit = defineEmits<{
  (e: 'update:selectedItem', item: any): void
}>()
const props = defineProps<Props>()
const selectionModel = computed({
  get() {
    return props.selectedItem
  },
  set(value: any) {
    emit('update:selectedItem', value)
  }
})
</script>

<style scoped></style>
