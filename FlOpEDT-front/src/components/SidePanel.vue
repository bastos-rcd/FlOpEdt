<template>
  <div class="side-panel" :class="{ open: authStore.sidePanelToggle }">
    <div>
      <h3>{{ $t('side.availabilityTitle') }}</h3>
      <Separator class="Separator" orientation="horizontal" />
      <div class="avail-div">
        <CheckboxRoot @update:checked="handleCheckboxClick" class="CheckboxRoot">
          <CheckboxIndicator class="CheckboxIndicator">
            <icon icon="iconoir:check"></icon>
          </CheckboxIndicator>
        </CheckboxRoot>
        {{ $t('side.availabilityLabel') }}
      </div>
    </div>
    <div class="workcopy-div">
      <h3>{{ $t('side.workcopyTitle') }}</h3>
      <Separator class="Separator" />
      <SelectRoot>
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
              <SelectItem v-for="n in 8" :value="n.toString()" class="SelectItem">
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
} from 'radix-vue'
import { Icon } from '@iconify/vue'
import { useI18n } from 'vue-i18n'
import { Separator } from 'radix-vue'
import { useAuth } from '@/stores/auth'
const { t } = useI18n()
const authStore = useAuth()
const emits = defineEmits<{
  (e: 'update:checkbox', v: boolean): void
}>()
function handleCheckboxClick(v: boolean) {
  emits('update:checkbox', v)
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
  width: 90%;
  background-color: white;
  height: 1px;
  margin: 0 0 8px 5px;
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
  box-shadow: 0px 10px 38px -10px rgba(22, 23, 24, 0.35), 0px 10px 20px -15px rgba(22, 23, 24, 0.2);
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
</style>
