<template>
    <router-link v-slot="{ href, isActive }" :to="to" custom>
        <v-list-item link :href="href" :active="isActive" :to="to">
            <template #prepend>
                <v-icon :icon="`mdi-${icon}`"></v-icon>
            </template>
            <v-list-item-title>{{ title }}</v-list-item-title>
        </v-list-item>
    </router-link>
</template>

<script lang="ts" setup>
defineProps<{
    title: string;
    icon: string;
    to: string;
}>();
</script>
