<template>
  <div id="full_logo">
    <a style="text-decoration: none; font-family: inherit; color: inherit" href="/">
      <span id="acro_logo"><span id="flopGreen">flop</span>!<span id="EDTRed">EDT</span></span>
    </a>
    <span id="head_logo"></span>
    <ChangeLocale></ChangeLocale>
    <a id="agpl" target="_blank" href="https://framagit.org/flopedt/flopedt">
      <img src="@/assets/images/agplv3-88x31.png" height="31" width="88" alt="AGPL v.3" />
    </a>
  </div>
  <Menu></Menu>
</template>

<script setup lang="ts">
import Menu from '@/components/Menu.vue'
import ChangeLocale from '@/components/utils/ChangeLocale.vue'
</script>

<style scoped>
#flopGreen {
  color: green;
  font-family: inherit;
  font-size: inherit;
}
#EDTRed {
  color: red;
  font-family: inherit;
  font-size: inherit;
}
#agpl {
  font-size: 10px;
  margin-left: auto;
  margin-top: 40px;
  margin-right: 10px;
  font-weight: 600;
}
#head_logo {
  font-size: 16px;
  font-family: 'Verdana';
  font-weight: bold;
  opacity: 0.7;
  margin-top: 45px;
  margin-left: 10px;
}
#full_logo {
  padding-top: 0px;
  font-family: 'flog';
  display: flex;
  flex-direction: row;
  color: black;
  align-items: center;
}
#acro_logo {
  font-size: 70px;
  font-family: inherit;
  font-weight: normal;
}
</style>
