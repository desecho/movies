<template>
  <v-app>
    <v-main>
      <MenuComponent />
      <ErrorBoundary context="Main Application" :allow-retry="true">
        <RouterView />
      </ErrorBoundary>
    </v-main>
    <FooterComponent />
  </v-app>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";

import { initAxios } from "./axios";
import ErrorBoundary from "./components/ErrorBoundary.vue";
import FooterComponent from "./components/FooterComponent.vue";
import MenuComponent from "./components/MenuComponent.vue";
import { useAuthStore } from "./stores/auth";
import { useThemeStore } from "./stores/theme";

const themeStore = useThemeStore();
const authStore = useAuthStore();

onMounted(async () => {
  // Initialize Vuetify theme integration
  themeStore.initVuetifyTheme();
  // Initialize theme preferences (auto-restored by plugin, set defaults for new users)
  themeStore.initTheme();

  // Initialize axios with authentication headers first
  if (authStore.user.isLoggedIn) {
    initAxios();

    // Now load avatar if user is logged in and doesn't have one
    if (!authStore.user.avatarUrl) {
      await authStore.loadAvatar();
    }
  }
});
</script>

<style>
@import "./styles/theme-variables.css";
@import "./styles/dark-theme-components.css";
@import "./styles/dark-theme-custom.css";
@import "./styles/dark-theme-typography.css";
@import "./styles/dark-theme-pagination.css";
@import "./styles/theme-transitions.css";
</style>
