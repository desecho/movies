<template>
  <div class="theme-toggle">
    <v-btn
      :icon="themeStore.isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
      variant="text"
      :title="`${themeStore.isDark ? 'Light' : 'Dark'} Mode (Vuetify Native + Custom)`"
      class="theme-toggle-btn"
      @click="themeStore.toggleTheme"
    >
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from "../stores/theme";

const themeStore = useThemeStore();
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-toggle-btn {
  transition: all 0.3s ease;
  border-radius: 50% !important;
  width: 40px !important;
  height: 40px !important;
}

.theme-toggle-btn:hover {
  background: rgba(var(--v-theme-primary), 0.1) !important;
  transform: scale(1.1);
}

:deep(.v-icon) {
  transition: all 0.3s ease;
}

.theme-toggle-btn:hover :deep(.v-icon) {
  transform: rotate(15deg);
}
</style>
