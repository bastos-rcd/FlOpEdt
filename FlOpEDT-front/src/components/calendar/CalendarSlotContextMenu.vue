<template>
  <div class="card p-0 m-0">
    <div class="card-body p-1 m-0">
      <div class="btn-group" role="group" aria-label="Slot context menu">
        <button type="button" class="btn btn-primary" @click="props.onEdit">Edit</button>
        <button type="button" class="btn btn-danger" @click="props.onDelete">Delete</button>
        <button type="button" class="btn btn-info" @click="props.onDuplicate">Duplicate</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  onEdit: () => void
  onDelete: () => void
  onDuplicate: () => void
}

const props = defineProps<Props>()
</script>

<script lang="ts">
export default {
  name: 'CalendarSlotContextMenu',
  components: {},
}
</script>

<style scoped></style>
