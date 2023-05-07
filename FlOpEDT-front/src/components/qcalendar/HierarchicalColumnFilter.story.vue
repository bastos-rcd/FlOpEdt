<template>
    <Story>
       <Variant title="Use case 1">
          <HierarchicalColumnFilter
            :columns="[]"
            :flatNodes="useCase1"
          />
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
            :flatNodes="useCase3"
          />
      </Variant>
    </Story>
</template>
  

<script setup lang="ts">
import HierarchicalColumnFilter from './HierarchicalColumnFilter.vue'
import { Tree, ITree } from '@/ts/tree'

const useCase1 = [
    {id: 5, name: "id5", parent:1},
    {id: 1, name: "id1", parent:null},
    {id: 2, name: "id2", parent:1},
    {id: 8, name: "id8", parent:5}
]
const useCase2 = [
    {id: 5, name: "id5", parent:1},
    {id: 1, name: "id1", parent:null},
    {id: 2, name: "id2", parent:1},
    {id: 3, name: "id3", parent:1},
    {id: 8, name: "id8", parent:5},
    {id: 9, name: "id9", parent:5}
]
const useCase3 = [
    {id: 1, name: "CE", parent:null},
    {id: 11, name: "TD1", parent:1},
    {id: 12, name: "TD2", parent:1},
    {id: 13, name: "TD3", parent:1},
    {id: 111, name: "TP1A", parent:11},
    {id: 112, name: "TP1B", parent:11},
    {id: 121, name: "TP2A", parent:12},
    {id: 122, name: "TP2B", parent:12},
    {id: 131, name: "TP3A", parent:13},
    {id: 132, name: "TP3B", parent:13}
]

</script>