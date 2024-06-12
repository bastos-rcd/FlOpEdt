<template>
  <div class="content">
    <div class="selector-header">
      <label>{{ props.filterSelectorUndefinedLabel }}</label>
      <CancelButton style="align-self: flex-end" @cancel-click="clearSelect" />
    </div>
    <div v-if="!multiple" class="simple-select">
      <select
        id="select"
        v-model="selectionModel"
        name="select"
        :multiple="props.multiple"
        class="select-content select"
      >
        <option v-for="(item, i) in itemsTyped" :key="i" :value="item">{{ item[itemVariableName] }}</option>
      </select>
    </div>
    <div v-else class="custom-dropdown select">
      <button class="selected-items select" :disabled="itemsTyped.length === 0" @click="toggleDropdown">
        <span v-if="Array.isArray(selectionModel) && selectionModel.length === 0">Select items...</span>
        <span
          v-if="Array.isArray(selectionModel)"
          >{{ selectionModel.map((el: any) => el[itemVariableName]).join(', ') }}</span
        >
      </button>
      <div class="dropdown-menu" :class="{ show: isDropdownOpen }">
        <label v-for="(item, i) in itemsTyped" :key="i">
          <input v-model="selectionModel" type="checkbox" :value="item" /> {{ item[itemVariableName] }}
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
  items: unknown[]
  filterSelectorUndefinedLabel: string
  selectedItems: unknown
  multiple: boolean
  itemVariableName: string
}

type DynamicPropertyType = {
  [key in typeof props.itemVariableName]: unknown
}

const itemsTyped = computed(() => {
  return props.items as DynamicPropertyType[]
})

const emit = defineEmits<{
  (e: 'update:selectedItems', item: unknown): void
}>()
const props = defineProps<Props>()
const selectionModel = computed({
  get() {
    return props.selectedItems
  },
  set(value: unknown) {
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
.selector-header {
  display: flex;
  justify-content: center;
  flex-direction: column-reverse;
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
  color: rgb(120, 120, 50);
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
@media screen and (max-width: 768px) {
  label {
    font-weight: normal;
    color: #000000;
  }
  .content {
    border: 1px solid #e3e3e3;
    border-radius: 10px;
    background-color: #ffffff;
    padding: 5px;
  }
  .selector-header {
    display: flex;
    justify-content: space-between;
    flex-direction: row;
    padding: 10px;
    align-items: center;
    border-bottom: 1px solid #e3e3e3;
  }
  .select-content {
    width: 30%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #fff;
    color: #000000;
    margin: 10px;
  }
  .custom-dropdown {
    margin: 10px;
  }
  .select:hover {
    background-color: transparent;
  }
  .selected-items {
    background-color: #ffffff;
    border: 1px solid #e3e3e3;
    color: #000000;
  }
  .selected-items:hover {
    background-color: #e5e5ff;
    border: 1px solid #4747b2;
    color: #4747b2;
  }
  .dropdown-menu {
    margin-top: 10px;
    color: #000000;
    border: 1px solid #e3e3e3;
  }
}
</style>
