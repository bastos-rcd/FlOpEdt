<template>

</template>

<script setup lang="ts">
import { useDepartmentStore } from '@/stores/department';
import { onMounted } from 'vue';

const deptStore = useDepartmentStore()

onMounted(() => {
    deptStore.fetchAllDepartments()
})
</script>