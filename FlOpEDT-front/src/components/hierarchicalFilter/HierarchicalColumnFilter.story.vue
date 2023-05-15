<template>
  <Story>
    <Variant :title="useCase1.title">
      <HierarchicalColumnFilter :active-ids="[]" :flatNodes="useCase1.flatNodes">
        <template #item="{ nodeId }">
          {{ find(useCase1.flatNodes, (n) => n.id === nodeId)?.name }}
        </template>
      </HierarchicalColumnFilter>
    </Variant>
    <Variant title="Default slot">
      <HierarchicalColumnFilter :active-ids="[]" :flatNodes="useCase2" />
    </Variant>
    <Variant title="Classical shape">
      <HierarchicalColumnFilter :active-ids="[]" :flatNodes="useCase3">
        <template #item="{ nodeId }">
          {{ find(useCase3, (n) => n.id === nodeId)?.name }}
        </template>
      </HierarchicalColumnFilter>
    </Variant>
    <Variant title="Interactive inside component">
      <HierarchicalColumnFilter v-model:active-ids="activeNodeIds" :flatNodes="useCase4.flatNodes">
        <!-- @update:activeIds="updateInPlace"> -->
        <template #item="{ nodeId, active }">
          <div :class="['node', active ? 'ac' : 'nac']">
            {{ find(useCase4.flatNodes, (n) => n.id === nodeId)?.name }}
            {{ active }}
          </div>
        </template>
      </HierarchicalColumnFilter>
    </Variant>
    <Variant title="Interactive from outside">
      <HierarchicalColumnFilter v-model:active-ids="activeNodeIds" :flatNodes="useCase4.flatNodes">
        <template #item="{ nodeId, active }">
          <div :class="['node', active ? 'ac' : 'nac']">
            {{ find(useCase4.flatNodes, (n) => n.id === nodeId)?.name }}
            {{ active }}
          </div>
        </template>
      </HierarchicalColumnFilter>
      <div>
        {{ activeNodeIds }}
      </div>
      <template v-for="nid in [111, 112, 121, 122, 131, 132]">
        <button @click="deactivate(nid)">Deactivate {{ find(useCase4.flatNodes, (n) => n.id == nid)?.name }}</button>
      </template>
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import HierarchicalColumnFilter from './HierarchicalColumnFilter.vue'
import { find, filter } from 'lodash'
import { ref } from 'vue'

const useCase1 = {
  title: 'Named with slots',
  flatNodes: [
    { id: 5, name: 'id5', parentId: 1 },
    { id: 1, name: 'id1', parentId: null },
    { id: 2, name: 'id2', parentId: 1 },
    { id: 8, name: 'id8', parentId: 5 },
  ],
}

const useCase2 = [
  { id: 5, name: 'id5', parentId: 1 },
  { id: 1, name: 'id1', parentId: null },
  { id: 2, name: 'id2', parentId: 1 },
  { id: 3, name: 'id3', parentId: 1 },
  { id: 8, name: 'id8', parentId: 5 },
  { id: 9, name: 'id9', parentId: 5 },
]
const useCase3 = [
  { id: 1, name: 'CE', parentId: null },
  { id: 11, name: 'TD1', parentId: 1 },
  { id: 12, name: 'TD2', parentId: 1 },
  { id: 13, name: 'TD3', parentId: 1 },
  { id: 111, name: 'TP1A', parentId: 11 },
  { id: 112, name: 'TP1B', parentId: 11 },
  { id: 121, name: 'TP2A', parentId: 12 },
  { id: 122, name: 'TP2B', parentId: 12 },
  { id: 131, name: 'TP3A', parentId: 13 },
  { id: 132, name: 'TP3B', parentId: 13 },
]

const activeNodeIds = ref([131, 121])

const useCase4 = {
  flatNodes: [
    { id: 1, name: 'CE', parentId: null },
    { id: 11, name: 'TD1', parentId: 1 },
    { id: 12, name: 'TD2', parentId: 1 },
    { id: 13, name: 'TD3', parentId: 1 },
    { id: 111, name: 'TP1A', parentId: 11 },
    { id: 112, name: 'TP1B', parentId: 11 },
    { id: 121, name: 'TP2A', parentId: 12 },
    { id: 122, name: 'TP2B', parentId: 12 },
    { id: 131, name: 'TP3A', parentId: 13 },
    { id: 132, name: 'TP3B', parentId: 13 },
  ],
}

function deactivate(id: number) {
  activeNodeIds.value = filter(activeNodeIds.value, (nid) => nid != id)
}
</script>

<style>
.node {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ac {
  background-color: rgba(25, 124, 25, 0.685);
}
.nac {
  background-color: rgb(133, 34, 34);
}
/* style="{width: 100 + '%'}" :style="active?{backgroundColor: 'green', height: 100 + '%'}:{backgroundColor: 'red'}" */
</style>

<docs lang="md">
# Welcome to a not-that-good doc

## Technical use

### Slots

`HierarchicalColumnFilter` component creates scoped slots, named `item`, whose scope is in
the form of `{nodeId: number, active: boolean}`. The slot content will be centered and
stretched inside the placeholder.

**Note:** the scope is reactive.

### Input/output

Clean `v-model` (I think).

- (Change in component => change in the caller environment) : see "Interactive inside component"
- (Change out of the component => change in the callee environment) : see "Interactive outside component"

**Note:** as the caller can pass an inconsistent list of active nodes
(_e.g._ an inactive parent node with children that are all active), we only
take into account in `props.activeNodeIds` the leaf nodes. The inconsistent
list in the caller component is changed by the `HierarchicalColumnFilter`
component into a consistent list.

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
