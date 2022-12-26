<template>
    <div>
        <h1>Back Page</h1>
    </div>
</template>
<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
    window.location.href = 'http://127.0.0.1:8000/'
})
</script>
