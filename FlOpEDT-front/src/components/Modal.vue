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
<style scoped>
</style>
