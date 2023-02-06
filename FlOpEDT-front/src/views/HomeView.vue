<template>
    <div>
        <h1>Welcome home !</h1>
    </div>
    <main class="text-center">
        <p v-if="deptStore.isCurrentDepartmentSelected">
            You are in department {{ deptStore.getCurrentDepartment.abbrev }}
        </p>
        <p v-else>
            Please select a department: <router-link :to="{name: routeNames.departmentSelection, params:{}}">Department Selection</router-link>
        </p>
    </main>
</template>

<script setup lang="ts">
import { useDepartmentStore } from '../stores/department'
import { routeNames } from '@/router/index'
const deptStore = useDepartmentStore()
</script>
