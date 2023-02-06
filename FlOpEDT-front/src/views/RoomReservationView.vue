<template>
    <div class="loader" v-if="loaderIsVisible"></div>
    <div>
        <h1>Welcome to the reservation page !</h1>
        <button @click='loaderTimer(1000)'>Show Loader</button>
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
import { ref } from 'vue'
import { useDepartmentStore } from '@/stores/department'

const authStore = useAuth()
const deptStore = useDepartmentStore()
const loaderIsVisible = ref(false)

function loaderTimer(timeout: number): void {
    loaderIsVisible.value = ! loaderIsVisible.value
    setTimeout(() => loaderIsVisible.value = !loaderIsVisible.value, timeout)
}
</script>

<style>
.loader {
    position: fixed;
    z-index: 9999;
    background: rgba(0, 0, 0, 0.6) url('@/assets/images/logo-head-gribou-rc-hand.svg') no-repeat 50% 50%;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    cursor: wait;
}
</style>