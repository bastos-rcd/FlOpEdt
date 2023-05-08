<template>
  <div class="wrapper" :style="styleContainer()">
    <template v-for="node in grid">
      <div class="item" :style="styleItem(node)">
        <span class="insider">
          <slot name="item" v-bind="{nodeId: node.id}">
              id: {{ node.id }}
          </slot>
        </span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, Ref } from 'vue'
import { CalendarColumn, GridCell, IdX } from './declaration'
import { Tree, ITree, TreeNode, LinkIdUp } from '@/ts/tree'
import { forEach } from 'lodash'

const nextColumns : CalendarColumn[] = []

const props = defineProps<{
    columns: CalendarColumn[]
    flatNodes: Array<LinkIdUp>
}>()

const emits = defineEmits<{
    (e: "update:columns", columns: CalendarColumn): void
}>()

const hierarchy = new Tree()
hierarchy.addNodes(props.flatNodes)

console.log(props.flatNodes)
console.log(hierarchy)



const grid : Ref<Array<GridCell>> = computed(() => {
  if (hierarchy.root === null) {
    return []
  }

  const cellList : Array<GridCell> = []

  const queue : Array<IdX> = [{id: hierarchy.root.id, xmin: 0}]
  while (queue.length != 0) {
    const cur = (queue.pop() as IdX)
    let curx = cur.xmin
    const tnode = hierarchy.byId[cur.id]
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


/*
plan:
v-model: ordered list of active columns?
props: hierarchical with all infos?

emit when finish traversing, a new array

*/



// function toggleActive(columnId: number) {
//   const col = props.columns.find(c => c.id === columnId)
//   if (col !== undefined) {
//     col.active = !col.active
//   }
// }

function styleItem(node : GridCell) {
  return("grid-area: " + (node.ymin + 1) + " / " + (node.xmin + 1) + " / "
        + (node.ymax + 2) + " / " + (node.xmax + 1))
}

function styleContainer() {
  return {
    gridTemplateColumns: 'repeat(' + hierarchy.root?.nLeaves + ', 1fr)'
  }
}
</script>

<style>
.wrapper {
  display: grid;
  grid-auto-rows: minmax(50px, auto);
}
/* Concise and accurate */
/* https://stackoverflow.com/questions/45536537/centering-in-css-grid */
.item {
  background-color: cornflowerblue;
  border-style: solid;
  display: flex;
}
.insider {
  margin: auto;
}
</style>