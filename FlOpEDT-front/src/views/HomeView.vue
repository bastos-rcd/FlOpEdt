<template>
    <div>
        <h1>Welcome home !</h1>
    </div>
    <main class="text-center">You are in department {{ deptStore.getCurrentDepartment.abbrev }}.</main>
</template>

<script setup lang="ts">
import { useDepartmentStore } from '../stores/department';
const deptStore = useDepartmentStore()
</script>
