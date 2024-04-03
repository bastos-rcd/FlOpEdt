<script setup lang="ts">
import { ToggleGroupItem, ToggleGroupRoot, CollapsibleContent, CollapsibleRoot, CollapsibleTrigger } from 'radix-vue'
import { computed, ref } from 'vue'
import { Icon } from '@iconify/vue'
const props = defineProps<{
  toggled: string[]
  calendarType: string
}>()
const emits = defineEmits<{
  (e: 'update:days', v: string[]): void
  (e: 'update:calendarType', v: string): void
}>()
const open = ref(false)
const toggledModel = computed({
  get() {
    return props.toggled
  },
  set(value: string[]) {
    if (value.length === 0) {
      value.push('mo')
    }
    emits('update:days', value)
  },
})
const calendarTypeModel = computed({
  get() {
    return props.calendarType
  },
  set(value: string) {
    emits('update:calendarType', value)
  },
})

function handleClick(days: string[]) {
  while (toggledModel.value.pop()) {
    /* empty */
  }
  toggledModel.value.push(...days)
}
</script>

<template>
  <CollapsibleRoot v-model:open="open">
    <div>
      <button class="ChoiceButtons" @click="calendarTypeModel = 'month'">
        {{ $t('periodPicker.typeMonth') }}
      </button>
      <button class="ChoiceButtons" @click="calendarTypeModel = 'week'">
        {{ $t('periodPicker.typeWeek') }}
      </button>
    </div>
    <div class="ChoiceButtons">
      <button @click="handleClick(['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su'])">
        {{ $t('periodPicker.allWeek') }}
      </button>
      <button @click="handleClick(['mo', 'tu', 'we', 'th', 'fr'])">{{ $t('periodPicker.mondayToFriday') }}</button>
    </div>
    <CollapsibleTrigger class="CollapsibleTrigger">
      <Icon v-if="open" icon="iconoir:collapse" width="1rem" height="1rem" class="Icon" />
      <Icon v-else icon="iconoir:expand-lines" width="1rem" height="1rem" class="Icon" />
    </CollapsibleTrigger>
    <CollapsibleContent>
      <ToggleGroupRoot v-model="toggledModel" type="multiple" class="ToggleGroup">
        <ToggleGroupItem value="mo" class="ToggleGroupItem"><span>mo</span> </ToggleGroupItem>
        <ToggleGroupItem value="tu" class="ToggleGroupItem"><span>tu</span> </ToggleGroupItem>
        <ToggleGroupItem value="we" class="ToggleGroupItem"><span>we</span> </ToggleGroupItem>
        <ToggleGroupItem value="th" class="ToggleGroupItem"><span>th</span> </ToggleGroupItem>
        <ToggleGroupItem value="fr" class="ToggleGroupItem"><span>fr</span> </ToggleGroupItem>
        <ToggleGroupItem value="sa" class="ToggleGroupItem"><span>sa</span> </ToggleGroupItem>
        <ToggleGroupItem value="su" class="ToggleGroupItem"><span>su</span> </ToggleGroupItem>
      </ToggleGroupRoot>
    </CollapsibleContent>
  </CollapsibleRoot>
</template>

<style scoped>
.ChoiceButtons {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 50px;
  padding: 2px;
  margin: 5px;
}
.ChoiceButtons button {
  padding: 2px;
  font-size: smaller;
  width: 60%;
  height: 40%;
  color: rgb(120, 120, 50);
}

.ChoiceButtons button:hover {
  border: 2px solid rgb(175, 175, 140);
  background-color: rgb(255, 255, 220);
}

.ToggleGroup {
  display: inline-flex;
  background-color: rgb(255, 255, 220);
  border-radius: 4px;
  box-shadow: 0 2px 10px black;
}

.ToggleGroupItem {
  background-color: white;
  color: rgb(128, 90, 0);
  height: 35px;
  width: 35px;
  display: flex;
  font-size: 15px;
  line-height: 1;
  align-items: center;
  justify-content: center;
  margin-left: 1px;
}
.ToggleGroupItem:first-child {
  margin-left: 0;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}
.ToggleGroupItem:last-child {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}
.ToggleGroupItem:hover {
  background-color: rgb(255, 255, 220);
}
.ToggleGroupItem[data-state='on'] {
  background-color: rgb(235, 235, 200);
  color: rgb(120, 120, 50);
}
.ToggleGroupItem:focus {
  position: relative;
  box-shadow: 0 0 0 2px black;
}
.CollapsibleTrigger {
  padding: 0;
  width: 30px;
  height: 30px;
}
.Icon {
  color: #9b6325;
}
</style>