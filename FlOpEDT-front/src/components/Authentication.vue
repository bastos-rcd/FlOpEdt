<template>
  <h3>{{ $t('authentication.title') }}</h3>
  <p>{{ $t('authentication.message') }}</p>
  <button @click="authStore.redirectLogin()">{{ $t('authentication.login-button') }}</button>
</template>

<script setup lang="ts">
import { useAuth } from '@/stores/auth'
const authStore = useAuth()
</script>

<style scoped>
h3 {
  font-weight: bolder;
  margin-top: 10px;
}
</style>
