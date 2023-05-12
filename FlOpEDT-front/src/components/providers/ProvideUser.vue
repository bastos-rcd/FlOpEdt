<template>
  <slot v-if="isUserLoaded"></slot>
  <div v-else>Chargement...</div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuth } from '@/stores/auth'

const authStore = useAuth()
const isUserLoaded = ref(false)

onMounted(async () => {
  await authStore.fetchAuthUser()
  isUserLoaded.value = true
})
</script>
