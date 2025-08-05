<template>
  <div>
    <v-app-bar v-if="isMobile" class="modern-app-bar" elevation="0">
      <v-app-bar-nav-icon variant="text" @click="toggleDrawer()"></v-app-bar-nav-icon>
      <v-app-bar-title class="app-title">
        <LogoComponent size="medium" variant="white" clickable navigate-to="/" />
      </v-app-bar-title>
      <template #append>
        <ThemeToggle />
      </template>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer" elevation="0" touchless>
      <div class="drawer-header">
        <LogoComponent size="large" variant="default" clickable navigate-to="/" />
      </div>
      <v-divider class="header-divider"></v-divider>
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
            <template v-if="user.isLoggedIn">
              <!-- User Profile Section -->
              <v-list-item class="user-profile-item mb-2">
                <template #prepend>
                  <UserAvatarComponent
                    :avatar-url="user.avatarUrl"
                    :username="user.username"
                    :size="40"
                    variant="outlined"
                  />
                </template>
                <v-list-item-title class="text-body-1 font-weight-medium">
                  {{ user.username }}
                </v-list-item-title>
              </v-list-item>

              <v-divider class="my-2"></v-divider>

              <MenuItem title="Settings" icon="cog" to="/preferences" />
              <MenuItem title="Logout" icon="logout" to="/logout" />
            </template>
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

import LogoComponent from "./LogoComponent.vue";
import MenuItem from "./MenuItem.vue";
import ThemeToggle from "./ThemeToggle.vue";
import UserAvatarComponent from "./UserAvatarComponent.vue";

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

.drawer-header {
  padding: 20px 16px 16px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.header-divider {
  background-color: rgba(0, 0, 0, 0.08);
  margin: 0 12px 8px;
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
  gap: 25px;
  padding: 8px 16px;
  margin: 0 -9px;
}

.theme-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #6b7280;
}

/* Dark theme drawer header */
:deep(.dark-theme) .drawer-header {
  background: rgba(55, 65, 81, 0.1);
}

:deep(.dark-theme) .header-divider {
  background-color: rgba(255, 255, 255, 0.1);
}

/* User profile section */
.user-profile-item {
  border-radius: 8px;
  background-color: rgba(102, 126, 234, 0.05);
  border: 1px solid rgba(102, 126, 234, 0.1);

  :deep(.v-list-item__prepend) {
    margin-right: 12px;
  }

  .v-list-item-title {
    font-weight: 600;
    color: rgb(var(--v-theme-on-surface));
  }
}

:deep(.dark-theme) .user-profile-item {
  background-color: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .drawer-header {
    padding: 16px 12px 12px;
  }
}
</style>
