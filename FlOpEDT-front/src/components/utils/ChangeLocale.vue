<template>
    <div>
        <label for="select-lang">{{ $t('language-selection|label') }}</label>
        <select id="select-lang" v-model="locale">
            <option v-for="currentLocale in availableLocales" :value="currentLocale">{{currentLocale}}</option>
        </select>
    </div>
</template>
    
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale, availableLocales } = useI18n({useScope: "global"})
</script>

<style scoped>
div {
    border-radius: 1px;
    border-color: black;
    border-style: solid;
    border-radius: 10px;
    height: 50%;
    padding: 5px;
    background: rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
}
select {
    width: 50%;
}
</style>