<template>
    <main class="text-center">You are in department {{ department }}.</main>
</template>

<script setup lang="ts">
import { getDepartment } from '@/main'

const department = getDepartment()
</script>
