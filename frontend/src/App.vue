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
  // Initialize theme preferences
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
/* Global Theme Variables */
:root {
  --background-primary: #ffffff;
  --background-secondary: #f8f9fa;
  --background-card: #ffffff;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --border-color: rgba(0, 0, 0, 0.05);
  --shadow-color: rgba(0, 0, 0, 0.08);
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
}

.dark-theme {
  --background-primary: #111827;
  --background-secondary: #1f2937;
  --background-card: #374151;
  --text-primary: #f9fafb;
  --text-secondary: #e5e7eb;
  --border-color: rgba(255, 255, 255, 0.1);
  --shadow-color: rgba(0, 0, 0, 0.3);
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
}

/* Apply theme variables globally */
.v-application {
  background: var(--background-primary) !important;
  color: var(--text-primary) !important;
}

/* Dark theme overrides for Vuetify components */
.dark-theme .v-app-bar {
  background: var(--gradient-primary) !important;
}

.dark-theme .v-navigation-drawer {
  background: var(--gradient-background) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .v-list-item {
  color: var(--text-primary) !important;
}

.dark-theme .v-list-item:hover {
  background-color: rgba(102, 126, 234, 0.2) !important;
}

.dark-theme .v-divider {
  border-color: var(--border-color) !important;
}

.dark-theme .v-text-field input {
  color: var(--text-primary) !important;
}

.dark-theme .v-text-field .v-field {
  background: var(--background-card) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .v-btn {
  color: var(--text-primary) !important;
}

.dark-theme .v-card {
  background: var(--background-card) !important;
  color: var(--text-primary) !important;
}

.dark-theme .v-footer {
  background: var(--background-secondary) !important;
  color: var(--text-secondary) !important;
  border-top: 1px solid var(--border-color) !important;
}

/* Dark theme for custom components */
.dark-theme .movie {
  background: var(--gradient-background) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .movie-card-content {
  background: var(--background-card) !important;
}

.dark-theme .title {
  color: var(--text-primary) !important;
}

.dark-theme .details {
  background: rgba(55, 65, 81, 0.8) !important;
  border-color: var(--border-color) !important;
  color: var(--text-secondary) !important;
}

.dark-theme .user-card {
  background: var(--gradient-background) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .page-header {
  background: var(--gradient-primary) !important;
}

.dark-theme .watch-count-item {
  background: rgba(55, 65, 81, 0.8) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .controls-section {
  background: rgba(55, 65, 81, 0.6) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .poster-rating {
  background: rgba(55, 65, 81, 0.9) !important;
  border-color: var(--border-color) !important;
}

/* Dark theme text colors */
.dark-theme .username {
  color: var(--text-primary) !important;
}

.dark-theme .user-subtitle {
  color: var(--text-secondary) !important;
}

.dark-theme .count-number {
  color: var(--text-primary) !important;
}

.dark-theme .count-label {
  color: var(--text-secondary) !important;
}

.dark-theme .item-desc {
  color: #d1d5db !important;
  font-weight: 600 !important;
}

.dark-theme .theme-label {
  color: var(--text-secondary) !important;
}

/* Enhanced text contrast for movie details in dark mode */
.dark-theme .details > div {
  color: #f3f4f6 !important;
}

.dark-theme .details .item-desc {
  color: #9ca3af !important;
  font-weight: 600 !important;
}

.dark-theme .movie-title {
  color: white !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
}

.dark-theme .page-title {
  color: white !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
}

.dark-theme .page-subtitle {
  color: rgba(255, 255, 255, 0.9) !important;
}

.dark-theme .section-title {
  color: var(--text-primary) !important;
}

.dark-theme .results-title {
  color: var(--text-primary) !important;
}

/* Improve readability for all text in dark mode */
.dark-theme {
  color: #f9fafb !important;
}

.dark-theme p,
.dark-theme span,
.dark-theme div {
  color: inherit;
}

.dark-theme .v-list-item-title {
  color: var(--text-primary) !important;
  font-weight: 500 !important;
}

/* Dark theme pagination styles for @hennge/vue3-pagination */
.dark-theme .pagination {
  --pagination-bg: rgba(55, 65, 81, 0.8);
  --pagination-text: #f9fafb;
  --pagination-hover-bg: rgba(102, 126, 234, 0.3);
  --pagination-border: rgba(255, 255, 255, 0.1);
}

.dark-theme .pagination .page-item {
  background: var(--pagination-bg) !important;
  color: var(--pagination-text) !important;
  border: 1px solid var(--pagination-border) !important;
}

.dark-theme .pagination .page-item:hover {
  background: var(--pagination-hover-bg) !important;
  border-color: #667eea !important;
  color: white !important;
}

.dark-theme .pagination .page-item.active {
  background: #667eea !important;
  color: white !important;
  border-color: #667eea !important;
}

.dark-theme .pagination .page-item.disabled {
  background: rgba(55, 65, 81, 0.5) !important;
  color: rgba(249, 250, 251, 0.5) !important;
  border-color: rgba(255, 255, 255, 0.05) !important;
}

/* Navigation arrows for @hennge/vue3-pagination */
.dark-theme .Pagination .Control {
  fill: white !important;
  opacity: 0.8;
}

.dark-theme .Pagination .Control-active {
  fill: white !important;
  opacity: 1;
}

.dark-theme .Pagination .Control-active:hover {
  fill: #667eea !important;
  opacity: 1;
}

/* Enhanced pagination control styling */

/* Smooth transitions for theme changes */
* {
  transition:
    background-color 0.3s ease,
    border-color 0.3s ease,
    color 0.3s ease;
}
</style>
