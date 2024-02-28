<template>
  <div class="content">
    <div style="display: flex; justify-content: center; flex-direction: column">
      <CancelButton @cancel-click="clearSelect" style="align-self: flex-end" />
      <label>{{ props.filterSelectorUndefinedLabel }}</label>
    </div>
    <div class="simple-select" v-if="!multiple">
      <select
        name="select"
        id="select"
        :multiple="props.multiple"
        class="select-content select"
        v-model="selectionModel"
      >
        <option v-for="item in items" :value="item">{{ item[itemVariableName] }}</option>
      </select>
    </div>
    <div class="custom-dropdown select" v-else>
      <button class="selected-items select" @click="toggleDropdown">
        <span v-if="selectionModel.length === 0">Select items...</span>
        <span v-else>{{ selectionModel.map((el: any) => el[itemVariableName]).join(', ') }}</span>
      </button>
      <div class="dropdown-menu" :class="{ show: isDropdownOpen }">
        <label v-for="item in items" :key="item.id">
          <input type="checkbox" :value="item" v-model="selectionModel" /> {{ item[itemVariableName] }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import CancelButton from './CancelButton.vue'

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
const isDropdownOpen = ref(false)

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value
}
function clearSelect() {
  if (props.multiple) {
    isDropdownOpen.value = false
    selectionModel.value = []
  } else selectionModel.value = undefined
}
</script>

<style scoped>
.content {
  display: flex;
  flex-direction: column;
}
label {
  font-weight: bolder;
}
.select:hover {
  background-color: rgb(255, 255, 220);
}
.custom-dropdown {
  display: inline-block;
}
.selected-items {
  padding: 8px;
  cursor: pointer;
  color: rgb(120, 120, 50);
  font-size: 15px;
}
.dropdown-menu {
  background-color: #fff;
  border: 1px solid #ccc;
  border-top: none;
  border-radius: 4px;
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
  display: none;
}
.dropdown-menu.show {
  display: block;
}
.dropdown-menu label {
  display: block;
  margin-bottom: 4px;
}
.dropdown-menu label input[type='checkbox'] {
  margin-right: 4px;
}
</style>
