<template>
    <Story>
       <Variant title="Named with slots">
          <HierarchicalColumnFilter
            :active-ids="[]"
            :flatNodes="useCase1">
              <template #item="{ nodeId }">
                {{ find(useCase1, n => n.id === nodeId)?.name }}
              </template>
          </HierarchicalColumnFilter>
      </Variant>
      <Variant title="Default slot">
          <HierarchicalColumnFilter
            :active-ids="[]"
            :flatNodes="useCase2"
          />
      </Variant>
      <Variant title="Classical shape">
        <HierarchicalColumnFilter
            :active-ids="[]"
            :flatNodes="useCase3">
              <template #item="{ nodeId }">
                {{ find(useCase3, n => n.id === nodeId)?.name }}
              </template>
          </HierarchicalColumnFilter>
      </Variant>
      <Variant title="Interactive">
        <HierarchicalColumnFilter
            :active-ids="recup"
            :flatNodes="useCase4.flatNodes"
            @update:activeIds="updateInPlace">
              <template #item="{ nodeId, active }">
                <div :class="['node', active?'ac':'nac']">
                <!-- <div :class="['node', find(activeNodeIds, nid => (nid==nodeId))?'ac':'nac']"> -->
                  {{ find(useCase4.flatNodes, n => (n.id === nodeId))?.name }}
                  {{ active }}
                  
                </div>
              </template>
          </HierarchicalColumnFilter>
      </Variant>
    </Story>
</template>
  

<script setup lang="ts">
import HierarchicalColumnFilter from './HierarchicalColumnFilter.vue'
import { Tree, ITree } from '@/ts/tree'
import { find, forEach } from 'lodash'
import { ref } from 'vue'

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

const activeNodeIds = [131, 121] //ref([131, 121])
let recup = ref([])

const useCase4 = {
  flatNodes: [
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
}

function updateInPlace(newActiveIds : Array<number>) {
  while(recup.value.length > 0) {
    recup.value.pop();
  }
  forEach((newActiveIds as Array<number>), id => {
    recup.value.push(id)
  })
}
</script>

<style>
.node {
  height: 100% ;
  width: 100% ;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ac {
  background-color:green
}
.nac {
  background-color:red
}
/* style="{width: 100 + '%'}" :style="active?{backgroundColor: 'green', height: 100 + '%'}:{backgroundColor: 'red'}" */
</style>

<docs lang="md">
  # Welcome

  ## Technical use
  `v-model`-like list
  ---
  
  Learn more about Histoire [here](https://histoire.dev/).
  </docs>