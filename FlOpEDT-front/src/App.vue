<template>
  <header>
    <Header></Header>
  </header>
  <main>
    <router-view></router-view>
  </main>
</template>

<script setup lang="ts">
import Header from '@/components/Header.vue'
import ProvideDepartment from '@/components/providers/ProvideDepartment.vue'
</script>

<style>
* {
  font-family: Arial, sans-serif;
}
h1 {
  font-size: 22px;
}
h2 {
  font-size: 20px;
}
h3 {
  font-size: 18px;
}
h4 {
  font-size: 16px;
}
</style>
