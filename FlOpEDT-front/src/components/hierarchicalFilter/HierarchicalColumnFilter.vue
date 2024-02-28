<template>
  <div>
    {{ $props.activeIds }}
  </div>
  <div class="wrapper" :style="styleContainer()">
    <template v-for="node in grid">
      <div class="item" :style="styleItem(node)" @click="toggle(node.id)">
        <slot name="item" v-bind="{ nodeId: node.id, active: indexOf($props.activeIds, node.id) > -1 }">
          id: {{ node.id }}
        </slot>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { GridCell } from './declaration'
import { Tree, LinkIdUp } from '@/ts/tree'
import { forEach, indexOf, cloneDeep, find, range, values, filter, sortBy } from 'lodash'

const props = defineProps<{
  activeIds: Array<number>
  flatNodes: Array<LinkIdUp>
}>()

const emits = defineEmits<{
  (e: 'update:activeIds', activeIds: Array<number>): void
}>()

const hierarchy = computed(() => {
  const tree = new Tree()
  tree.addNodes(props.flatNodes, props.activeIds)
  tree.adjustDepth()
  tree.distributeWeight()
  tree.sortFamily()
  updateActiveIds(tree.getActiveIds())
  return tree
})

function updateActiveIds(newValue: Array<number>) {
  let hasChanged = false
  if (props.activeIds.length != newValue.length) {
    hasChanged = true
  } else {
    if (find(props.activeIds, (nid, i) => props.activeIds[i] != newValue[i]) !== undefined) {
      hasChanged = true
    }
  }
  if (hasChanged) {
    emits('update:activeIds', newValue)
  }
}

const grid = computed(() => {
  if (hierarchy.value.roots.length == 0) {
    return []
  }

  const cellList: Array<GridCell> = []

  forEach(range(hierarchy.value.depth + 1), (d) => {
    const filtered = filter(values(hierarchy.value.byId), (node) => node.depthMin <= d && node.depthMax >= d)
    const sorted = sortBy(filtered, (node) => node.rank)
    let preWeight = 0
    forEach(sorted, (node) => {
      const newCell = {
        id: node.id,
        xmin: preWeight,
        xmax: preWeight + node.weight,
        ymin: node.depthMin,
        ymax: node.depthMax + 1,
      }
      const prev = find(cellList, (cell) => cell.id == node.id)
      if (prev === undefined) {
        cellList.push(newCell)
      } else {
        if (prev.xmin != preWeight) {
          throw new Error('Most probably the groups are not given in the right order...')
        }
      }
      preWeight += node.weight
    })
  })

  return cellList
})

function styleItem(node: GridCell) {
  return 'grid-area: ' + (node.ymin + 1) + ' / ' + (node.xmin + 1) + ' / ' + (node.ymax + 1) + ' / ' + (node.xmax + 1)
}

function styleContainer() {
  return {
    gridTemplateColumns: 'repeat(' + hierarchy.value.weight + ', 1fr)',
  }
}

function toggle(id: number) {
  // deep clone not needed, but maybe cleaner since hierarchy is computed
  const tree = cloneDeep(hierarchy.value)
  tree.byId[id].toggleActive()
  updateActiveIds(tree.getActiveIds())
}
</script>

<style>
.wrapper {
  display: grid;
  grid-auto-rows: minmax(50px, auto);
  gap: 0;
}
/* Concise and accurate */
/* https://stackoverflow.com/questions/45536537/centering-in-css-grid */
.item {
  background-color: cornflowerblue;
  border-style: solid;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
