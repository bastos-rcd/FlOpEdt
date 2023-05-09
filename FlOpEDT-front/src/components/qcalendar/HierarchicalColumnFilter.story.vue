<template>
    <Story>
       <Variant :title="useCase1.title">
          <HierarchicalColumnFilter
            :active-ids="[]"
            :flatNodes="useCase1.flatNodes">
              <template #item="{ nodeId }">
                {{ find(useCase1.flatNodes, n => n.id === nodeId)?.name }}
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
            :active-ids="activeNodeIds"
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

const useCase1 = {
  title: "Named with slots",
  flatNodes: [
    {id: 5, name: "id5", parentId:1},
    {id: 1, name: "id1", parentId:null},
    {id: 2, name: "id2", parentId:1},
    {id: 8, name: "id8", parentId:5}
  ]
}

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

const activeNodeIds = ref([131, 121])

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
  while(activeNodeIds.value.length > 0) {
    activeNodeIds.value.pop();
  }
  forEach((newActiveIds as Array<number>), id => {
    activeNodeIds.value.push(id)
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
  background-color:rgba(25, 124, 25, 0.685)
}
.nac {
  background-color:rgb(133, 34, 34)
}
/* style="{width: 100 + '%'}" :style="active?{backgroundColor: 'green', height: 100 + '%'}:{backgroundColor: 'red'}" */
</style>

<docs lang="md">
  # Welcome to a not-that-good doc

  ## Technical use
  ### Slots
  `HierarchicalColumnFilter` component creates scoped slots, named `item`, whose scope is
  `{nodeId: number, active: boolean}`. The slot content will be centered and stretched inside
  the placeholder.
  Note: the scope is reactive.

  ### Input/output
  The `activeIds` should be seen as a `v-model`-like list. As it is an object, I think we
  cannot use the default `v-model` way because it would cycle: the parent component gives
  a list as a property, then `HierarchicalColumnFilter` computes an updated list and emits
  an `update:activeIds` event with the new value, then the parent component changes its
  list accordingly. But this update, in the calling component, changed the pointer to the list,
  even if the list content did not change.
  Hence:
  - in the calling component, we cut the cycle by pouring the new value into the list, while
  not changing the pointer
  - in `HierarchicalColumnFilter`, we keep a local list, so that if the calling component does
  not implement the previous point, we are still reactive in the component.

  ## User interface
  - Click on a node => toggle activation (except specific case where all nodes are active)
  - "Nobody is active" is a transient state that resolves into "Everybody is active"

  ## TODO
  - The aesthetics should be improved (gaps, remove the tiny margins that appear in blue),
  and I guess slots should help.
  - The style may not be clean (I'm quite ignorant for now): should we scope something?
  
  ---
  
  Learn more about Histoire [here](https://histoire.dev/).
  </docs>