<template>
    <main class="text-center">
        <h1>Please select a department</h1>
        <div class="container w-50">
            <div v-if="departments">
                <div v-for="department in departments" :key="department.id" class="row mb-1">
                    <router-link
                        :to="{
                            name: routeNames.home,
                            params: { dept: department.abbrev },
                        }"
                        class="btn btn-dark"
                        role="button"
                    >
                        {{ department.abbrev }}
                    </router-link>
                </div>
            </div>
        </div>
    </main>
</template>

<script setup lang="ts">
import { apiKey, requireInjection } from '@/assets/js/keys'
import type { Department } from '@/assets/js/types'
import { routeNames } from '@/router'
import { ref } from 'vue'

const api = requireInjection(apiKey)
const departments = ref<Array<Department>>()
api.fetch.all.departments().then((value) => (departments.value = value))
</script>
