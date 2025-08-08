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

/* High specificity styles for profile list selector buttons */
.profile-header .profile-list-selector :deep(.v-btn-toggle) {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.profile-header .profile-list-selector :deep(.v-btn-toggle .v-btn) {
  color: white !important;
  background: rgba(255, 255, 255, 0.25) !important;
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
  backdrop-filter: blur(10px) !important;
  font-weight: 600 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
  min-width: 80px !important;
}

.profile-header .profile-list-selector :deep(.v-btn-toggle .v-btn:hover) {
  background: rgba(255, 255, 255, 0.4) !important;
  color: white !important;
  border-color: rgba(255, 255, 255, 0.6) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
}

.profile-header .profile-list-selector :deep(.v-btn-toggle .v-btn.v-btn--active) {
  background: white !important;
  color: #667eea !important;
  border-color: white !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  font-weight: 700 !important;
  text-shadow: none !important;
}

/* Alternative approach with direct class targeting */
:deep(.profile-btn-toggle) {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

:deep(.profile-btn-toggle .v-btn) {
  color: white !important;
  background: rgba(255, 255, 255, 0.25) !important;
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
  backdrop-filter: blur(10px) !important;
  font-weight: 600 !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
  min-width: 80px !important;
}

:deep(.profile-btn-toggle .v-btn:hover) {
  background: rgba(255, 255, 255, 0.4) !important;
  color: white !important;
  border-color: rgba(255, 255, 255, 0.6) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
}

:deep(.profile-btn-toggle .v-btn.v-btn--active) {
  background: white !important;
  color: #667eea !important;
  border-color: white !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  font-weight: 700 !important;
  text-shadow: none !important;
}
</style>