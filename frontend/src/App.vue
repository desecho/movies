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
import { useSEO } from "./composables/useSEO";
import { useOrganizationStructuredData } from "./composables/useStructuredData";
import { useAuthStore } from "./stores/auth";
import { useThemeStore } from "./stores/theme";

// Default SEO for the entire application
useSEO({
  title: "MovieMunch",
  description:
    "Track what you watch. Discover what to watch next. Join the MovieMunch community for personalized movie recommendations and discover your next favorite film.",
  keywords: ["movies", "film", "cinema", "watch", "tracking", "recommendations", "moviemunch"],
  type: "website",
  url: "/",
});

// Organization structured data
useOrganizationStructuredData({
  name: "MovieMunch",
  description:
    "The ultimate movie tracking platform. Create watchlists, get AI recommendations, follow friends, and discover your next favorite film.",
  url: "https://moviemunch.org",
  logo: "https://moviemunch.org/img/logo.png",
  sameAs: ["https://github.com/desecho/movies"],
});

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
