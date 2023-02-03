<template>
    <div>
        <h1>Welcome to the reservation page !</h1>
    </div>
    <div v-if="authStore.isUserAuthenticated">
        <p>L'utilisateur est connecté : {{ authStore.getUser.first_name }}</p>
    </div>
    <div v-else>
        <p>L'utilisateur n'est pas connecté.</p>
        <button @click="authStore.redirectLogin()">Login</button>
    </div>

</template>

<script setup lang="ts">
import { useAuth } from '@/stores/auth'
const authStore = useAuth()
</script>

<style>

</style>