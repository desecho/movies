<template>
  <div>
    <v-app-bar v-if="isMobile" class="modern-app-bar" elevation="0">
      <v-app-bar-nav-icon variant="text" @click="toggleDrawer()"></v-app-bar-nav-icon>
      <v-app-bar-title class="app-title">
        <span class="title-gradient">Movies</span>
      </v-app-bar-title>
      <template #append>
        <ThemeToggle />
      </template>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer" width="200" elevation="0" class="modern-drawer" touchless>
      <v-list class="nav-list" density="comfortable">
        <MenuItem title="Search" icon="magnify" to="/" />
        <MenuItem title="Trending" icon="trending-up" to="/trending" />
        <MenuItem v-if="user.isLoggedIn" title="Watched" icon="eye" to="/list/watched" />
        <MenuItem v-if="user.isLoggedIn" title="ToWatch" icon="eye-off" to="/list/to-watch" />
        <MenuItem title="Users" icon="account-group" to="/users" />
      </v-list>
      <template #append>
        <div class="drawer-footer">
          <v-divider class="mb-3"></v-divider>
          <div class="theme-toggle-container">
            <ThemeToggle />
            <span class="theme-label">{{ themeStore.isDark ? "Dark Mode" : "Light Mode" }}</span>
          </div>
          <v-divider class="my-3"></v-divider>
          <v-list class="nav-list" density="comfortable">
            <MenuItem v-if="!user.isLoggedIn" title="Login" icon="login" to="/login" />
            <MenuItem v-if="user.isLoggedIn" title="Settings" icon="cog" to="/preferences" />
            <MenuItem v-if="user.isLoggedIn" title="Logout" icon="logout" to="/logout" />
          </v-list>
        </div>
      </template>
    </v-navigation-drawer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, toRef } from "vue";

import { useMobile } from "../composables/mobile";
import { useAuthStore } from "../stores/auth";
import { useThemeStore } from "../stores/theme";

import MenuItem from "./MenuItem.vue";
import ThemeToggle from "./ThemeToggle.vue";

const drawer = ref(false);
const userStore = useAuthStore();
const user = toRef(userStore, "user");
const themeStore = useThemeStore();

function toggleDrawer(): void {
  drawer.value = !drawer.value;
}

const { isMobile } = useMobile();

onMounted(() => {
  if (!isMobile.value) {
    drawer.value = true;
  }
});
</script>

<style scoped>
.modern-app-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.app-title {
  font-weight: 700;
}

.title-gradient {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.modern-drawer {
  background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%) !important;
  border-right: 1px solid rgba(0, 0, 0, 0.08);
}

.nav-list {
  padding: 8px 12px;

  :deep(.v-list-item) {
    border-radius: 8px;
    margin-bottom: 4px;
    transition: all 0.2s ease;

    &:hover {
      background-color: rgba(102, 126, 234, 0.1);
      transform: translateX(4px);
    }

    &.v-list-item--active {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;

      .v-list-item__prepend .v-icon,
      .v-list-item-title {
        color: white;
      }
    }

    .v-list-item__prepend {
      .v-icon {
        font-size: 20px;
        opacity: 0.8;
      }
    }

    .v-list-item-title {
      font-weight: 500;
      font-size: 0.95rem;
    }
  }
}

.drawer-footer {
  padding: 0 12px 16px;

  .v-divider {
    background-color: rgba(0, 0, 0, 0.08);
  }
}

.theme-toggle-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 8px 16px;
  margin: 0 -4px;
}

.theme-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #6b7280;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .modern-drawer {
    width: 280px !important;
  }
}
</style>
