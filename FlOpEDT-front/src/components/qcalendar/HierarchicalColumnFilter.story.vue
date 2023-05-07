<template>
    <Story>
       <Variant title="Use case 1">
          <HierarchicalColumnFilter
            :columns="[]"
            :flatNodes="useCase1">
              <template #item="{ nodeId }">
                {{ find(useCase1, n => n.id === nodeId)?.name }}
              </template>
          </HierarchicalColumnFilter>
      </Variant>
      <Variant title="Use case 2">
          <HierarchicalColumnFilter
            :columns="[]"
            :flatNodes="useCase2"
          />
      </Variant>
      <Variant title="Use case 3">
        <HierarchicalColumnFilter
            :columns="[]"
            :flatNodes="useCase3">
              <template #item="{ nodeId }">
                {{ find(useCase3, n => n.id === nodeId)?.name }}
              </template>
          </HierarchicalColumnFilter>
      </Variant>
    </Story>
</template>
  

<script setup lang="ts">
import HierarchicalColumnFilter from './HierarchicalColumnFilter.vue'
import { Tree, ITree } from '@/ts/tree'
import { find } from 'lodash'

const useCase1 = [
    {id: 5, name: "id5", parentId:1},
    {id: 1, name: "id1", parentId:null},
    {id: 2, name: "id2", parentId:1},
    {id: 8, name: "id8", parentId:5}
]

const useCase2 = [
    {id: 5, name: "id5", parentId:1},
    {id: 1, name: "id1", parentId:null},
    {id: 2, name: "id2", parentId:1},
    {id: 3, name: "id3", parentId:1},
    {id: 8, name: "id8", parentId:5},
    {id: 9, name: "id9", parentId:5}
]
const useCase3 = [
    {id: 1, name: "CE", parentId:null},
    {id: 11, name: "TD1", parentId:1},
    {id: 12, name: "TD2", parentId:1},
    {id: 13, name: "TD3", parentId:1},
    {id: 111, name: "TP1A", parentId:11},
    {id: 112, name: "TP1B", parentId:11},
    {id: 121, name: "TP2A", parentId:12},
    {id: 122, name: "TP2B", parentId:12},
    {id: 131, name: "TP3A", parentId:13},
    {id: 132, name: "TP3B", parentId:13}
]

</script>