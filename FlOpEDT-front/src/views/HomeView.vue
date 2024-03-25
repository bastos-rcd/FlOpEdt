<template>
  <section>
    <h1>{{ $t('home.welcome') }}</h1>
    <div v-if="deptStore.isCurrentDepartmentSelected">
      <p>{{ $t('home.department-message') }} {{ deptStore.current.abbrev }}</p>
      <button @click="deptStore.cleanCurrentDepartment()">{{ $t('home.department-button-change') }}</button>
    </div>
    <DepartmentSelection v-else />
  </section>
</template>

<script setup lang="ts">
import { useDepartmentStore } from '@/stores/department'
import DepartmentSelection from '@/components/DepartmentSelection.vue'
const deptStore = useDepartmentStore()
</script>
