<template>
<input v-model="emailadress" id="email" @input="updateEmail()"/>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const emailadress = ref("")
</script>

<style>
</style>