<template>
  <!-- Filters -->
  <div class="col">
    <!-- Room filter -->
    <div class="row mb-3">
      <FilterSelector
        filterSelectorLabel="roomreservation.sidebar.rooms"
        filterSelectorUndefinedLabel="roomreservation.sidebar.rooms-label"
        itemVariableName="name"
        :selectedItem="selectedRoom"
        :items="filterRoomstoDisplay"
        @itemSelected="(newRoom: Room) => emit('selectedRoomChange', newRoom)"
      >
      </FilterSelector>
    </div>
    <!-- Department filter -->
    <!--:items="departmentStore.getAllDepartmentsFetched"-->
    <div class="row mb-3">
      <FilterSelector
        filterSelectorLabel="roomreservation.sidebar.department"
        filterSelectorUndefinedLabel="roomreservation.sidebar.department-label"
        itemVariableName="abbrev"
        :selectedItem="selectedDepartment"
        :items="departmentStore.getAllDepartmentsFetched"
        @itemSelected="(newDept: Department) => emit('selectedDepartmentChange', newDept)"
      >
      </FilterSelector>
    </div>
    <!-- Room attribute and name filters -->
    <div v-if="!selectedRoom" class="row">
      <div class="mb-3">
        <ClearableInput
          :input-id="'filter-input-roomName'"
          :label="`${$t('roomreservation.sidebar.room-filter')}`"
          v-model:text="roomNameFilter"
        ></ClearableInput>
      </div>
      <!--
            <div class="mb-3">
                <DynamicSelect
                    v-bind="{
                        id: 'filter-select-attribute',
                        label: $t('roomreservation.sidebar.option-filter'),
                        values: createFiltersValues(),
                    }"
                    v-model:selected-values="selectedRoomAttributes"
                ></DynamicSelect>
            </div>
            -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Department, Room } from '@/ts/type'
import { useRoomStore } from '@/stores/room'
import { computed, ref } from 'vue'
import { useDepartmentStore } from '@/stores/department'
import FilterSelector from '@/components/utils/FilterSelector.vue'
import ClearableInput from '@/components/utils/ClearableInput.vue'
import { watch } from 'vue'

interface Props {
  selectedRoom: Room | undefined
  selectedDepartment: Department | undefined
}
const emit = defineEmits<{
  (e: 'selectedRoomChange', room: Room): void
  (e: 'selectedDepartmentChange', dept: Department): void
  (e: 'roomNameFilterChange', newRoomNameFilter: string): void
}>()

const props = defineProps<Props>()
const roomStore = useRoomStore()
const departmentStore = useDepartmentStore()
const roomNameFilter = ref('')
const { t } = useI18n()

const filterRoomstoDisplay = computed(() => {
  return roomStore.rooms
    .filter((r: Room) => {
      if (props.selectedDepartment) {
        let belongsToDept = false
        if (r.departments.length === 0) {
          belongsToDept = true
        } else {
          r.departments.forEach((dept: Department) => {
            if (dept.id === props.selectedDepartment?.id) {
              belongsToDept = true
            }
          })
        }
        return (r.is_basic && belongsToDept) || r.departments.length === 0
      }
      return r.is_basic
    })
    .sort((r1: Room, r2: Room) => {
      return r1.name.toLowerCase().localeCompare(r2.name.toLowerCase())
    })
})

watch(roomNameFilter, (newName, oldName) => {
  emit('roomNameFilterChange', newName)
})

/*
function createFiltersValues(): Array<RoomAttributeEntry> {
    const out = []

    out.push(
        ...roomAttributes.booleanList.value.map((attribute) => {
            return {
                component: markRaw(DynamicSelectedElementBoolean),
                value: {
                    id: attribute.id,
                    name: attribute.name,
                    value: false,
                },
            }
        })
    )
    out.push(
        ...roomAttributes.numericList.value.map((attribute) => {
            const values = roomAttributeValues.numericList.value
                .filter((att) => att.attribute === attribute.id)
                .map((att) => att.value)
            const min = Math.min(...values)
            const max = Math.max(...values)
            return {
                component: markRaw(DynamicSelectedElementNumeric),
                value: {
                    id: attribute.id,
                    name: attribute.name,
                    min: min,
                    max: max,
                    initialMin: min,
                    initialMax: max,
                },
            }
        })
    )
    return out
}*/
</script>

<style scoped></style>
