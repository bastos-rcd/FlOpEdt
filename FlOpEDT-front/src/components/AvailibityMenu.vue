<template>
  <ContextMenuRoot>
    <ContextMenuTrigger>
      <slot name="trigger">
        <div class="trigger-content">
          <span>Right-Click Here !</span>
        </div>
      </slot>
    </ContextMenuTrigger>
    <ContextMenuContent>
      <slot name="content">
        <ContextMenuRadioGroup :v-model="valueModel">
          <ContextMenuRadioItem v-for="n in 8" :key="n" :value="n.toString()" @select="handleSelection(n)">
            {{ n }}
          </ContextMenuRadioItem>
        </ContextMenuRadioGroup>
      </slot>
    </ContextMenuContent>
  </ContextMenuRoot>
</template>

<script setup lang="ts">
import {
  ContextMenuContent,
  ContextMenuRadioGroup,
  ContextMenuRadioItem,
  ContextMenuRoot,
  ContextMenuTrigger,
} from 'radix-vue'
import { computed } from 'vue'

const props = defineProps<{
  value: number
}>()
const emits = defineEmits<{
  (e: 'update:value', v: number): void
}>()

//Value V-MODEL
const valueModel = computed({
  get() {
    return props.value
  },
  set(v: number) {
    emits('update:value', v)
  },
})
function handleSelection(n: number) {
  valueModel.value = n
}
</script>
