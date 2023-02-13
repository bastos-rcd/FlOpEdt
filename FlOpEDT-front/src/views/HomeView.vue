<template>
    <div>
        <h1>Welcome to FlOpEDT !</h1>
    </div>
    <main class="text-center">
        <div v-if="deptStore.isCurrentDepartmentSelected">
            <p>
                You are in department {{ deptStore.getCurrentDepartment.abbrev }}
            </p>
            <button @click="deptStore.cleanCurrentDepartment()">Change Department</button>
        </div>
        <DepartmentSelection v-else/>
    </main>
</template>

<script setup lang="ts">
import { useDepartmentStore } from '@/stores/department'
import DepartmentSelection from '@/components/DepartmentSelection.vue';
import { onMounted } from 'vue';
const deptStore = useDepartmentStore()

onMounted(() => {
    if(!deptStore.isCurrentDepartmentSelected) {
        deptStore.getDepartmentFromURL()
    }
})
</script>
