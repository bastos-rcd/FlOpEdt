<template>
    <section>
        <h1>Welcome to FlOpEDT !</h1>
        <div v-if="deptStore.isCurrentDepartmentSelected">
            <p>
                You are in department {{ deptStore.getCurrentDepartment.abbrev }}
            </p>
            <button @click="deptStore.cleanCurrentDepartment()">Change Department</button>
        </div>
        <DepartmentSelection v-else/>
    </section>
</template>

<script setup lang="ts">
import { useDepartmentStore } from '@/stores/department'
import DepartmentSelection from '@/components/DepartmentSelection.vue';
const deptStore = useDepartmentStore()
</script>
