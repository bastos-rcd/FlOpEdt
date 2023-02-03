<template>
    <main class="text-center">
        <h1>Please select a department</h1>
        <div class="container w-50">
            <div v-if="deptStore.getAllDepartments.length !== 0">
                <div v-for="department in deptStore.getAllDepartments" :key="department.id" class="row mb-1">
                    <router-link
                        :to="{
                            name: routeNames.home,
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
