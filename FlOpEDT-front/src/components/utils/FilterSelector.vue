<template>
    <label for="select-item" class="form-label">{{ $t(filterSelectorLabel) }}</label>
    <div v-if="newSelection" class="col-auto pe-0">
        <button type="button" class="btn-close" @click="handleCrossClick"></button>
    </div>
    <div class="col-auto">
        <select
            id="select-item"
            v-model="newSelection"
            class="form-select w-auto"
            aria-label="Select Item"
        >
            <option :value="undefined">{{ $t(filterSelectorUndefinedLabel) }}</option>
            <option
                v-for="item in props.items"
                :key="item.id"
                :value="item"
            >
                {{ item[props.itemVariableName] }}
            </option>
        </select>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

/*
 *  items : list of objects we can chose in the selector
 *  filterSelectorLabel : text label displayed above the selector box
 *  filterSelectorUndefinedLabel : default text label inside selector box
 *  selectedItem : The current selectedItem if it has been changed by parent
 *  itemVariableName: attribute name of the objects.
 **/
interface Props {
    items: any[],
    filterSelectorLabel : string,
    filterSelectorUndefinedLabel : string,
    selectedItem : any,
    itemVariableName : string
}

const emit = defineEmits<{
    (e: 'itemSelected', item: any): void
}>()
const props = defineProps<Props>()
const newSelection = ref<any>()

/*
 *  When the data is changed inside the component
 *  we notify the parent and sent it the
 *  new value.
 **/
watch( newSelection, (newSelectedItem) => {
    emit('itemSelected', newSelectedItem)
})

/*
 *  When the parent changes the data we are
 *  notified through the props.
 **/
watch(() => props.selectedItem, () => {
    if(newSelection.value === undefined || props.selectedItem.id !== newSelection.value.id) {
        newSelection.value = props.selectedItem
    }
})

/*
 *  When we click on the component cross
 *  it clears the data.
 **/
function handleCrossClick() {
    newSelection.value = undefined
}

</script>

<style scoped>

</style>