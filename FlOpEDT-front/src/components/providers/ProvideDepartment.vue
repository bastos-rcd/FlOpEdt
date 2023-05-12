<template>
  <slot v-if="departmentsLoaded"></slot>
  <div v-else>Chargement...</div>
</template>

<script setup lang="ts">
import { useDepartmentStore } from '@/stores/department'
import { onMounted, ref } from 'vue'

const deptStore = useDepartmentStore()
const departmentsLoaded = ref(false)

onMounted(async () => {
  await deptStore.fetchAllDepartments()
  departmentsLoaded.value = true
})
</script>
