<template>
  <main class="text-center">
    <h2>{{ $t('department-selection.title') }}</h2>
    <div class="container w-50">
      <div v-if="deptStore.all.length !== 0">
        <div v-for="department in deptStore.all" :key="department.id" class="row mb-1">
          <router-link
            :to="{
              name: routeNames.home,
              params: { dept: department.abbrev },
            }"
            class="choices"
            @click="deptStore.current = new Department(department.id, department.abbrev)"
          >
            {{ department.abbrev }}
          </router-link>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { routeNames } from '@/router'
import { useDepartmentStore } from '@/stores/department'
import { Department } from '@/ts/type'

const deptStore = useDepartmentStore()
</script>

<style scoped>
.choices {
  font-weight: bold;
  margin-bottom: 3px;
}
</style>
