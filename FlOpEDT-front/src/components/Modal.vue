<template>
  <div class="GroupSelect">
    <FilterSelector
      v-model:selectedItems="groupsSelected"
      :multiple="false"
      :items="props.groups"
      filter-selector-undefined-label="Choisissez un groupe"
      item-variable-name="name"
    />
  </div>
</template>
<script setup lang='ts'>
import FilterSelector from './utils/FilterSelector.vue'
import { Group } from '@/stores/declarations'
import { storeToRefs } from 'pinia'
import { useGroupStore } from '@/stores/timetable/group'

const groupStore = useGroupStore()

const { groupsSelected } = storeToRefs(groupStore)
const props = defineProps<{
  groups: Group[]
}>()
</script>
<style>
h3 {
  font-weight: bolder;
  font-size: large;
}
.side-panel {
  border-top: 1px solid white;
  min-width: 15%;
  color: white;
  background-color: #333;
  z-index: 5;
}
.avail-div {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.CheckboxRoot {
  background-color: white;
  width: 25px;
  height: 25px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgb(230, 230, 230);
}
.CheckboxRoot:hover {
  background-color: rgb(255, 255, 220);
}
.CheckboxRoot:focus {
  box-shadow: 0 0 0 2px white;
}
.CollapsibleTrigger {
  padding: 0;
  width: 30px;
  height: 30px;
}
.CheckboxIndicator {
  color: rgb(120, 120, 50);
}
.workcopy-div {
  margin-top: 10px;
}
.Separator {
  width: 100%;
  background-color: white;
  height: 1px;
  margin: 5px 0 8px 0;
}
.SelectTrigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  margin-right: 5px;
  margin-left: 5px;
  padding: 0 15px;
  font-size: 13px;
  line-height: 1;
  height: 35px;
  gap: 5px;
  background-color: white;
  color: rgb(150, 150, 0);
  box-shadow: 0 2px 10px rgb(230, 230, 230);
}
.SelectTrigger:hover {
  background-color: rgb(255, 250, 230);
}
.SelectTrigger:focus {
  box-shadow: 0 0 0 2px rgb(240, 240, 240);
}
.SelectContent {
  overflow: hidden;
  background-color: white;
  border-radius: 6px;
  box-shadow:
    0px 10px 38px -10px rgba(22, 23, 24, 0.35),
    0px 10px 20px -15px rgba(22, 23, 24, 0.2);
}
.SelectViewport {
  padding: 5px;
}
.SelectItem {
  font-size: 13px;
  line-height: 1;
  color: rgb(100, 100, 0);
  border-radius: 3px;
  display: flex;
  align-items: center;
  height: 25px;
  padding: 0 35px 0 25px;
  position: relative;
  user-select: none;
}
.SelectItem[data-disabled] {
  color: rgb(80, 80, 80);
  pointer-events: none;
}
.SelectItem[data-highlighted] {
  outline: none;
  background-color: rgb(255, 245, 200);
  color: rgb(200, 200, 120);
}
.SelectLabel {
  padding: 0 25px;
  font-size: 12px;
  line-height: 25px;
  color: rgb(175, 150, 30);
}
.SelectItemIndicator {
  position: absolute;
  left: 0;
  width: 25px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
