<template>
  <ProvideUser></ProvideUser>
  <ProvideDepartment></ProvideDepartment>
  <Header></Header>
  <router-view></router-view>
</template>

<script setup lang="ts">
import ProvideUser from '@/components/providers/ProvideUser.vue';
import Header from '@/components/Header.vue';
import ProvideDepartment from '@/components/providers/ProvideDepartment.vue';

</script>
