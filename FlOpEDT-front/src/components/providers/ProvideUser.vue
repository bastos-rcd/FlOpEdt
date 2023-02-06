<template>

</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuth } from '@/stores/auth'

const authStore = useAuth()

onMounted(() => {
  authStore.fetchAuthUser()
})

</script>