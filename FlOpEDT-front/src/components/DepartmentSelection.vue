<template>
    <main class="text-center">
        <h2>Please select a department</h2>
        <div class="container w-50">
            <div v-if="deptStore.getAllDepartmentsFetched.length !== 0">
                <div v-for="department in deptStore.getAllDepartmentsFetched" :key="department.id" class="row mb-1">
                    <router-link
                        :to="{
                            name: routeNames.home,
                            params: {}
                        }"
                        @click.native="deptStore.setCurrentDepartment(new Department(department.id, department.abbrev))">
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
