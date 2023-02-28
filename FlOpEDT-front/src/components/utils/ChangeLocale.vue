<template>
    <select v-model="locale">
        <option value="en">en</option>
        <option value="es">es</option>
        <option value="fr">fr</option>
    </select>
</template>
    
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale } = useI18n({useScope: "global"})
</script>