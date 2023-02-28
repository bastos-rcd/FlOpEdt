<template>
<div>
    <p>{{ $t("authentication.message") }}</p>
    <button @click="authStore.redirectLogin()">{{ $t("authentication.login-button") }}</button>
</div>
</template>

<script setup lang="ts">
import { useAuth } from '@/stores/auth';
import { useI18n } from 'vue-i18n';

const t = useI18n()
const authStore = useAuth()
</script>

<style scoped>
</style>