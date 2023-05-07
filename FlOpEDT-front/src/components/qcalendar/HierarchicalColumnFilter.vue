<template>
  <!-- <div>
    {{ grid }}
  </div> -->
  <div class="wrapper" :style="styleContainer()">
    <template v-for="node in grid">
      <div class="item" :style="styleItem(node)">
        <span class="insider">
          {{ node.id }}
          {{ styleItem(node) }}
        </span>
      </div>
    </template>

    <!-- <div class="item"
    style="grid-column: 1 / 3;
           grid-row: 1 / 3;">
      
      <div> aze</div>
      <div> aze</div>
      <div> aze</div>
      <div> aze</div>

    </div>
    <div class="item"
    style="grid-area: 1 / 2 / 3 / 3;">ert</div>
    <div class="item">ertzz</div>
    <div class="item">ertaa</div>
    <div class="item">era</div>
    <div class="item">a</div> -->
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { CalendarColumn } from './declaration'
import { Tree, ITree, TreeNode } from '@/ts/tree'
import { forEach } from 'lodash'

const nextColumns : CalendarColumn[] = []

const props = defineProps<{
    columns: CalendarColumn[]
    flatNodes: Array<{id: number, name: string, parent: number | null}>
}>()

const emits = defineEmits<{
    (e: "update:columns", columns: CalendarColumn): void
}>()

const hierarchy = new Tree<{id:number, name:string, parent:number|null}>()
hierarchy.addNodes(props.flatNodes)

console.log(props.flatNodes)
console.log(hierarchy)


const grid = computed(() => {
  const nodeList = []
  const queue = [{id: hierarchy.root?.data.id, xmin: 0}]
  while (queue.length != 0) {
    const cur = queue.pop()
    let curx = cur.xmin
    const tnode = hierarchy.byId[cur.id]
    forEach(tnode.children, child => {
      queue.push({id: child.data.id, xmin:curx})
      curx += child.nLeaves
    })

    nodeList.push({
      id: cur.id,
      xmin: cur.xmin,
      xmax: curx,
      ymin: tnode.depthMin,
      ymax: tnode.depthMax,
    })
  }
  return(nodeList)
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

function styleItem(node) {
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