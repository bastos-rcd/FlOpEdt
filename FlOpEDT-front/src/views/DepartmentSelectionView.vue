<template>
    <main class="text-center">
        <h1>Please select a department</h1>
        <div class="container w-50">
            <div v-if="departments">
                <div v-for="department in departments" :key="department.id" class="row mb-1">
                    <router-link
                        :to="{
                            name: routeNames.home,
                            params: { dept: department.abbrev },
                        }"
                        class="btn btn-dark"
                        role="button"
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
import { useDepartmentStore, type Department } from '@/stores/department'
import { ref } from 'vue'

const deptStore = useDepartmentStore()
const departments = ref<Array<Department>>()
deptStore.remote.fetch().then(() => {
    departments.value = deptStore.departments
})
</script>
