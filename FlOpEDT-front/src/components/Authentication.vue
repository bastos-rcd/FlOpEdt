<template>
<div>
    <p>Please login to access this page:</p>
    <button @click="authStore.redirectLogin()">Login</button>
</div>
</template>

<script setup lang="ts">
import { useAuth } from '@/stores/auth';

const authStore = useAuth()
</script>

<style scoped>
</style>