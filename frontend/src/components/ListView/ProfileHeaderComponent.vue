<template>
  <v-row>
    <v-col cols="12">
      <div class="profile-header">
        <div class="profile-user-info">
          <UserAvatarComponent
            :avatar-url="userAvatarUrl"
            :username="username"
            :size="80"
            variant="elevated"
            class="profile-avatar"
          />
          <h2>{{ username }}'s Movies</h2>
        </div>
        <!-- List selector for profile views -->
        <div class="profile-list-selector">
          <v-btn-toggle
            :model-value="selectedList"
            density="compact"
            mandatory
            class="profile-btn-toggle"
            @update:model-value="$emit('update:selectedList', $event)"
          >
            <v-btn :value="listWatchedId" :size="modeButtonSize"> Watched </v-btn>
            <v-btn :value="listToWatchId" :size="modeButtonSize"> To Watch </v-btn>
          </v-btn-toggle>
        </div>
      </div>
    </v-col>
  </v-row>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import { useMobile } from "../../composables/mobile";
import { listToWatchId, listWatchedId } from "../../const";
import UserAvatarComponent from "../UserAvatarComponent.vue";

interface Props {
  username: string;
  userAvatarUrl: string | null;
  selectedList: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:selectedList": [listId: number];
}>();

const { isMobile } = useMobile();

const modeButtonSize = computed(() => {
  if (isMobile.value) {
    return "small";
  }
  return "default";
});
</script>

<style scoped>
.profile-header {
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.profile-user-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.profile-user-info h2 {
  margin: 0;
  color: white;
  font-size: 2rem;
  font-weight: 700;
}

.profile-avatar {
  flex-shrink: 0;
}

.profile-list-selector {
  display: flex;
  justify-content: center;
}

/* Ultra-high specificity styles for profile list selector buttons - override everything */
.profile-header .profile-list-selector :deep(.v-btn-group.v-btn-toggle) {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  border-radius: 8px !important;
}

.profile-header .profile-list-selector :deep(.v-btn-group.v-btn-toggle .v-btn) {
  color: white !important;
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(10px) !important;
  font-weight: 600 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
  min-width: 80px !important;
  margin: 6px;
}

.profile-header .profile-list-selector :deep(.v-btn-group.v-btn-toggle .v-btn:hover) {
  background: rgba(255, 255, 255, 0.25) !important;
  color: white !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
}

.profile-header .profile-list-selector :deep(.v-btn-group.v-btn-toggle .v-btn.v-btn--active) {
  background: white !important;
  color: #667eea !important;
  border-color: white !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  font-weight: 700 !important;
  text-shadow: none !important;
  margin: 6px;
}

/* Force override dark theme styles with maximum specificity */
.profile-header :deep(.profile-btn-toggle.v-btn-toggle) {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  border-radius: 8px !important;
}

.profile-header :deep(.profile-btn-toggle.v-btn-toggle .v-btn) {
  color: white !important;
  background: rgba(255, 255, 255, 0.25) !important;
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
  backdrop-filter: blur(10px) !important;
  font-weight: 600 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
  min-width: 80px !important;
}

.profile-header :deep(.profile-btn-toggle.v-btn-toggle .v-btn:hover) {
  background: rgba(255, 255, 255, 0.4) !important;
  color: white !important;
  border-color: rgba(255, 255, 255, 0.6) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
}

.profile-header :deep(.profile-btn-toggle.v-btn-toggle .v-btn.v-btn--active) {
  background: white !important;
  color: #667eea !important;
  border-color: white !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  font-weight: 700 !important;
  text-shadow: none !important;
}

/* Nuclear option - override EVERYTHING with ultra-high specificity */
.profile-header .profile-list-selector :deep(.profile-btn-toggle),
.profile-header .profile-list-selector :deep(.v-btn-toggle),
.profile-header .profile-list-selector :deep(.v-btn-group) {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
  border-radius: 8px !important;
  gap: 8px !important;
}

.profile-header .profile-list-selector :deep(.profile-btn-toggle .v-btn),
.profile-header .profile-list-selector :deep(.v-btn-toggle .v-btn),
.profile-header .profile-list-selector :deep(.v-btn-group .v-btn) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  font-weight: 600 !important;
  min-width: 80px !important;
}

.profile-header .profile-list-selector :deep(.profile-btn-toggle .v-btn:hover),
.profile-header .profile-list-selector :deep(.v-btn-toggle .v-btn:hover),
.profile-header .profile-list-selector :deep(.v-btn-group .v-btn:hover) {
  background: rgba(255, 255, 255, 0.25) !important;
  color: white !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
}

.profile-header .profile-list-selector :deep(.profile-btn-toggle .v-btn.v-btn--active),
.profile-header .profile-list-selector :deep(.v-btn-toggle .v-btn.v-btn--active),
.profile-header .profile-list-selector :deep(.v-btn-group .v-btn.v-btn--active) {
  background: white !important;
  color: #667eea !important;
  border-color: white !important;
  font-weight: 700 !important;
}
</style>
