<template>
  <ContextMenuRoot :modal="false">
    <ContextMenuTrigger class="ContextMenuTrigger" as="div">
      <slot name="trigger">
        <span>Right-Click Here !</span>
      </slot>
    </ContextMenuTrigger>
    <ContextMenuPortal>
      <ContextMenuContent>
        <ContextMenuRadioGroup :v-model="props.event.data.value" class="ContextMenuRadioGroup">
          <ContextMenuRadioItem
            v-for="n in 8"
            :key="n"
            :value="n.toString()"
            @select="handleSelection(n)"
            class="ContextMenuRadioItem"
          >
            {{ n }}
          </ContextMenuRadioItem>
        </ContextMenuRadioGroup>
      </ContextMenuContent>
    </ContextMenuPortal>
  </ContextMenuRoot>
</template>

<script setup lang="ts">
import {
  ContextMenuContent,
  ContextMenuPortal,
  ContextMenuRadioGroup,
  ContextMenuRadioItem,
  ContextMenuRoot,
  ContextMenuTrigger,
} from 'radix-vue'
import { CalendarEvent } from './calendar/declaration'
const props = defineProps<{
  event: CalendarEvent
}>()
const emits = defineEmits<{
  (e: 'update:event', id: number, value: number): void
}>()

function handleSelection(n: number) {
  emits('update:event', props.event.id, n)
}
</script>

<style>
.ContextMenuRadioItem {
  margin: 5px;
  background-color: rgb(220, 220, 220);
}
.ContextMenuRadioItem:hover {
  background-color: rgb(245, 245, 245);
}
.ContextMenuRadioGroup {
  background-color: white;
  border-radius: 2%;
  border: 1px solid rgb(220, 220, 220);
  min-height: 150px;
  min-width: 100px;
}
.ContextMenuTrigger {
  background-color: rgba(255, 255, 255, 0);
  border-radius: 10px;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.ContextMenuContent {
  z-index: 5;
}
</style>
