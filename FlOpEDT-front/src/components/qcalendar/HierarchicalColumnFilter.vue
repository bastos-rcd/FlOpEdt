<template>
  <div class="wrapper" :style="styleContainer()">
    <template v-for="node in grid">
      <div class="item" :style="styleItem(node)" @click="toggle(node.id)">
          <slot name="item" v-bind="{nodeId: node.id, active: indexOf(localActiveIds, node.id) > -1}">
              id: {{ node.id }}
          </slot>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, Ref } from 'vue'
import { CalendarColumn, GridCell, IdX } from './declaration'
import { Tree, ITree, TreeNode, LinkIdUp } from '@/ts/tree'
import { forEach, map, filter, values, indexOf, difference } from 'lodash'

const nextColumns : CalendarColumn[] = []



const props = defineProps<{
    activeIds: Array<number>
    flatNodes: Array<LinkIdUp>
}>()

const emits = defineEmits<{
    (e: "update:activeIds", activeIds: Array<number>): void
}>()

const hierarchy = computed(() => {
  const tree = new Tree()
  tree.addNodes(props.flatNodes, props.activeIds)
  updateActiveIds(tree)
  return tree
})

const localActiveIds = ref(props.activeIds)

function updateActiveIds(tree: Tree) {
  const newValue = map(filter(values(tree.byId), node => node.active), node => {
    return node.id
  })
  localActiveIds.value = newValue
  emits("update:activeIds", newValue)
}



console.log(props.flatNodes)
console.log(hierarchy.value)



const grid = computed(() => {
  console.log("grid aussi")
  if (hierarchy.value.root === null) {
    return []
  }

  const cellList : Array<GridCell> = []

  const queue : Array<IdX> = [{id: hierarchy.value.root.id, xmin: 0}]
  while (queue.length != 0) {
    const cur = (queue.pop() as IdX)
    let curx = cur.xmin
    const tnode = hierarchy.value.byId[cur.id]
    forEach(tnode?.children, child => {
      queue.push({id: child.id, xmin:curx})
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
  return(cellList)
})


function styleItem(node : GridCell) {
  return("grid-area: " + (node.ymin + 1) + " / " + (node.xmin + 1) + " / "
        + (node.ymax + 2) + " / " + (node.xmax + 1))
}

function styleContainer() {
  return {
    gridTemplateColumns: 'repeat(' + hierarchy.value.root?.nLeaves + ', 1fr)'
  }
}

function toggle(id: number) {
  hierarchy.value.byId[id].toggleActive()
  updateActiveIds(hierarchy.value)
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