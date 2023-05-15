<template>
  <q-select
    clearable
    :multiple="props.multiple"
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
 *  selectedItems : The current selectedItem
 * * if multiple is true, it is an array of items
 * * else, it is just an object
 *  multiple: trigger multiple select
 *  itemVariableName: attribute name of the objects.
 **/
interface Props {
  items: any[]
  filterSelectorUndefinedLabel: string
  selectedItems: any | null
  multiple: boolean
  itemVariableName: string
}

const emit = defineEmits<{
  (e: 'update:selectedItems', item: any): void
}>()
const props = defineProps<Props>()
const selectionModel = computed({
  get() {
    return props.selectedItems
  },
  set(value: any) {
    emit('update:selectedItems', value)
  },
})
</script>

<style scoped></style>
