<template>
  <ProvideUser>
    <ProvideDepartment>
      <header>
        <Header></Header>
      </header>
      <main>
        <router-view></router-view>
      </main>
    </ProvideDepartment>
  </ProvideUser>
</template>

<script setup lang="ts">
import ProvideUser from '@/components/providers/ProvideUser.vue';
import Header from '@/components/Header.vue';
import ProvideDepartment from '@/components/providers/ProvideDepartment.vue';
</script>

<style>
* {
  font-family: Arial, sans-serif;
  alignment-baseline:middle;
  dominant-baseline:middle;
}
h1 {
  font-size:22px;
}
h2 {
  font-size:20px;
}
h3 {
  font-size:18px;
}
h4 {
  font-size:16px;
}
body{
    background: linear-gradient(to bottom, rgb(176,176,176), rgb(255,255,255));
}
</style>
