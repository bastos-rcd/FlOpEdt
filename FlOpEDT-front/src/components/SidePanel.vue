<template>
  <div class="side-panel" :class="{ open: authStore.sidePanelToggle }">
    <div class="RevertButton">
      <Separator class="Separator" />
      <span>Revert Changes </span>
      <button :disabled="!revert" @click="handleClick"><Icon icon="iconoir:undo-circle" /></button>
    </div>
    <div>
      <h3>{{ $t('side.availabilityTitle') }}</h3>
      <Separator class="Separator" orientation="horizontal" />
      <div class="avail-div">
        <CheckboxRoot v-model:checked="availCheckBox" class="CheckboxRoot" :default-checked="availCheckBox">
          <CheckboxIndicator class="CheckboxIndicator">
            <Icon icon="iconoir:check"></Icon>
          </CheckboxIndicator>
        </CheckboxRoot>
        {{ $t('side.availabilityLabel') }}
      </div>
    </div>
    <div class="workcopy-div">
      <h3>{{ $t('side.workcopyTitle') }}</h3>
      <Separator class="Separator" />
      <SelectRoot v-model="workcopy">
        <SelectTrigger class="SelectTrigger">
          <SelectValue :placeholder="$t('side.workcopyPlaceholder')" />
          <Icon icon="iconoir:nav-arrow-down" />
        </SelectTrigger>
        <SelectContent class="SelectContent">
          <SelectScrollUpButton class="SelectScrollButton">
            <Icon icon="iconoir:nav-arrow-up" />
          </SelectScrollUpButton>
          <SelectViewport class="SelectViewport">
            <SelectLabel class="SelectLabel">
              {{ $t('side.workcopyNumber') }}
            </SelectLabel>
            <SelectGroup>
              <SelectItem v-for="n in 8" :key="n" :value="n.toString()" class="SelectItem">
                <SelectItemIndicator class="SelectItemIndicator">
                  <Icon icon="iconoir:check" />
                </SelectItemIndicator>
                <SelectItemText>
                  {{ n }}
                </SelectItemText>
              </SelectItem>
            </SelectGroup>
          </SelectViewport>
          <SelectScrollDownButton class="SelectScrollButton">
            <Icon icon="iconoir:nav-arrow-up" />
          </SelectScrollDownButton>
        </SelectContent>
      </SelectRoot>
    </div>
    <div class="GroupSelect">
      <Separator class="Separator" />
      <FilterSelector
        v-model:selectedItems="groupsSelected"
        :multiple="true"
        :items="props.groups"
        filter-selector-undefined-label="Groups to display"
        item-variable-name="name"
      />
    </div>
    <div class="RoomSelect">
      <Separator class="Separator" />
      <FilterSelector
        v-model:selectedItems="roomsSelected"
        :multiple="true"
        :items="props.rooms"
        filter-selector-undefined-label="Filter Rooms"
        item-variable-name="name"
      />
    </div>
    <div class="TutorSelect">
      <Separator class="Separator" />
      <FilterSelector
        v-model:selectedItems="tutorsSelected"
        :multiple="true"
        :items="props.tutors"
        filter-selector-undefined-label="Filter teachers"
        item-variable-name="username"
      />
    </div>
    <div class="ModuleSelect">
      <Separator class="Separator" />
      <FilterSelector
        v-model:selected-items="modulesSelected"
        :multiple="true"
        :items="modules"
        filter-selector-undefined-label="Module Filter"
        item-variable-name="abbrev"
      />
    </div>
    <div class="CourseTypeSelect">
      <Separator class="Separator" />
      <FilterSelector
        v-model:selected-items="courseTypesSelected"
        :multiple="true"
        :items="courseTypeIds"
        filter-selector-undefined-label="Course type Filter"
        item-variable-name="id"
      />
    </div>
    <div class="ColorSelect">
      <Separator class="Separator" />
      <h3>Coloration Select</h3>
      <RadioGroupRoot v-model="colorSelect" class="RadioGroupRoot" default-value="module">
        <div :style="{ display: 'flex', alignItems: 'center' }">
          <RadioGroupItem id="r1" class="RadioGroupItem" value="module">
            <RadioGroupIndicator class="RadioGroupIndicator" />
          </RadioGroupItem>
          <label class="Label" for="r1"> module </label>
        </div>
        <div :style="{ display: 'flex', alignItems: 'center' }">
          <RadioGroupItem id="r2" class="RadioGroupItem" value="courseType">
            <RadioGroupIndicator class="RadioGroupIndicator" />
          </RadioGroupItem>
          <label class="Label" for="r2"> Course Type </label>
        </div>
      </RadioGroupRoot>
    </div>
  </div>
</template>
<script setup lang="ts">
import {
  CheckboxIndicator,
  CheckboxRoot,
  SelectContent,
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectScrollUpButton,
  SelectViewport,
  SelectLabel,
  SelectGroup,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectScrollDownButton,
  RadioGroupRoot,
  RadioGroupItem,
  RadioGroupIndicator,
} from 'radix-vue'
import { Icon } from '@iconify/vue'
import { Separator } from 'radix-vue'
import { useAuth } from '@/stores/auth'
import { computed } from 'vue'
import FilterSelector from './utils/FilterSelector.vue'
import { Group, Room, User } from '@/stores/declarations'
import { useEventStore } from '@/stores/display/event'
import { storeToRefs } from 'pinia'
import { useGroupStore } from '@/stores/timetable/group'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { usePermanentStore } from '@/stores/timetable/permanent'
const authStore = useAuth()
const eventStore = useEventStore()
const groupStore = useGroupStore()
const courseStore = useScheduledCourseStore()
const permanentStore = usePermanentStore()
const availCheckBox = computed({
  get() {
    return props.availChecked
  },
  set(v: boolean) {
    emits('update:checkbox', v)
  },
})
const workcopy = computed({
  get() {
    return props.workcopy.toString()
  },
  set(v: string) {
    emits('update:workcopy', Number(v))
  },
})
const { roomsSelected, tutorsSelected, colorSelect, courseTypesSelected } = storeToRefs(eventStore)
const { modules, modulesSelected } = storeToRefs(permanentStore)
const { groupsSelected } = storeToRefs(groupStore)
const { courseTypeIds } = storeToRefs(courseStore)
const props = defineProps<{
  availChecked: boolean
  workcopy: number
  rooms: Room[]
  tutors: User[]
  groups: Group[]
  revert: boolean
}>()
const emits = defineEmits<{
  (e: 'update:checkbox', v: boolean): void
  (e: 'update:workcopy', v: number): void
  (e: 'update:rooms', v: Room[]): void
  (e: 'revertUpdate'): void
}>()

function handleClick() {
  emits('revertUpdate')
}
</script>
<style>
h3 {
  font-weight: bolder;
  font-size: large;
}
.side-panel {
  border-top: 1px solid white;
  min-width: 15%;
  color: white;
  background-color: #333;
  z-index: 5;
}
.avail-div {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.CheckboxRoot {
  background-color: white;
  width: 25px;
  height: 25px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgb(230, 230, 230);
}
.CheckboxRoot:hover {
  background-color: rgb(255, 255, 220);
}
.CheckboxRoot:focus {
  box-shadow: 0 0 0 2px white;
}

.CheckboxIndicator {
  color: rgb(120, 120, 50);
}
.workcopy-div {
  margin-top: 10px;
}
.Separator {
  width: 100%;
  background-color: white;
  height: 1px;
  margin: 5px 0 8px 0;
}
.SelectTrigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  margin-right: 5px;
  margin-left: 5px;
  padding: 0 15px;
  font-size: 13px;
  line-height: 1;
  height: 35px;
  gap: 5px;
  background-color: white;
  color: rgb(150, 150, 0);
  box-shadow: 0 2px 10px rgb(230, 230, 230);
}
.SelectTrigger:hover {
  background-color: rgb(255, 250, 230);
}
.SelectTrigger:focus {
  box-shadow: 0 0 0 2px rgb(240, 240, 240);
}
.SelectContent {
  overflow: hidden;
  background-color: white;
  border-radius: 6px;
  box-shadow:
    0px 10px 38px -10px rgba(22, 23, 24, 0.35),
    0px 10px 20px -15px rgba(22, 23, 24, 0.2);
}
.SelectViewport {
  padding: 5px;
}
.SelectItem {
  font-size: 13px;
  line-height: 1;
  color: rgb(100, 100, 0);
  border-radius: 3px;
  display: flex;
  align-items: center;
  height: 25px;
  padding: 0 35px 0 25px;
  position: relative;
  user-select: none;
}
.SelectItem[data-disabled] {
  color: rgb(80, 80, 80);
  pointer-events: none;
}
.SelectItem[data-highlighted] {
  outline: none;
  background-color: rgb(255, 245, 200);
  color: rgb(200, 200, 120);
}
.SelectLabel {
  padding: 0 25px;
  font-size: 12px;
  line-height: 25px;
  color: rgb(175, 150, 30);
}
.SelectItemIndicator {
  position: absolute;
  left: 0;
  width: 25px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.SelectScrollButton {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 25px;
  background-color: white;
  color: rgb(30, 30, 30);
  cursor: default;
}
.RadioGroupRoot {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px;
}
.RadioGroupItem {
  background-color: white;
  width: 25px;
  height: 25px;
  border-radius: 100%;
  box-shadow: 0 2px 10px #222;
  padding: 0;
}
.RadioGroupItem:hover {
  background-color: #cc7;
}
.RadioGroupItem:focus {
  box-shadow: 0 0 0 2px black;
}
.RadioGroupIndicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  position: relative;
}
.RadioGroupIndicator::after {
  content: '';
  display: block;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background-color: #aa5;
}
.Label {
  color: white;
  font-size: 15px;
  line-height: 1;
  padding-left: 15px;
}
.RevertButton {
  margin-bottom: 10px;
}
.RevertButton button {
  padding: 0;
  border-radius: 10%;
}
</style>
