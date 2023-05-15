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
import { GridCell, IdX } from './declaration'
import { Tree, LinkIdUp } from '@/ts/tree'
import { forEach, indexOf, cloneDeep, find } from 'lodash'

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
  if (hierarchy.value.root === null) {
    return []
  }

  const cellList: Array<GridCell> = []

  const queue: Array<IdX> = [{ id: hierarchy.value.root.id, xmin: 0 }]
  while (queue.length != 0) {
    const cur = queue.pop() as IdX
    let curx = cur.xmin
    const tnode = hierarchy.value.byId[cur.id]
    forEach(tnode?.children, (child) => {
      queue.push({ id: child.id, xmin: curx })
      curx += child.nLeaves
    })

    cellList.push({
      id: cur.id,
      xmin: cur.xmin,
      xmax: curx,
      ymin: tnode.depthMin,
      ymax: tnode.depthMax,
    })
  }
  return cellList
})

function styleItem(node: GridCell) {
  return 'grid-area: ' + (node.ymin + 1) + ' / ' + (node.xmin + 1) + ' / ' + (node.ymax + 2) + ' / ' + (node.xmax + 1)
}

function styleContainer() {
  return {
    gridTemplateColumns: 'repeat(' + hierarchy.value.root?.nLeaves + ', 1fr)',
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
