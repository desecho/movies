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
          <div class="profile-text-info">
            <h2>{{ username }}'s Movies</h2>
            <div v-if="followStatus" class="follow-stats">
              <router-link 
                :to="`/users/${username}/followers`"
                class="follow-stat-link"
              >
                {{ followStatus.followers_count }} followers
              </router-link>
              •
              <router-link 
                :to="`/users/${username}/following`"
                class="follow-stat-link"
              >
                {{ followStatus.following_count }} following
              </router-link>
            </div>
          </div>
          
          <!-- Follow Button -->
          <div v-if="authStore.user.isLoggedIn && authStore.user.username !== username" class="follow-button-wrapper">
            <v-btn
              :loading="followLoading"
              :color="followStatus?.is_following ? 'success' : 'white'"
              :variant="followStatus?.is_following ? 'outlined' : 'elevated'"
              size="large"
              @click="toggleFollow"
              class="follow-btn-profile"
            >
              <v-icon 
                :icon="followStatus?.is_following ? 'mdi-account-check' : 'mdi-account-plus'" 
                start 
              />
              {{ followStatus?.is_following ? 'Following' : 'Follow' }}
            </v-btn>
          </div>
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
import axios from "axios";
import { computed, onMounted, ref } from "vue";

import type { Ref } from "vue";

import { useMobile } from "../../composables/mobile";
import { listToWatchId, listWatchedId } from "../../const";
import { getUrl } from "../../helpers";
import { useAuthStore } from "../../stores/auth";
import { $toast } from "../../toast";
import UserAvatarComponent from "../UserAvatarComponent.vue";

interface FollowStatus {
  is_following: boolean;
  followers_count: number;
  following_count: number;
}

interface Props {
  username: string;
  userAvatarUrl: string | null;
  selectedList: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:selectedList": [listId: number];
}>();

const authStore = useAuthStore();
const { isMobile } = useMobile();

const followStatus: Ref<FollowStatus | null> = ref(null);
const followLoading = ref(false);

const modeButtonSize = computed(() => {
  if (isMobile.value) {
    return "small";
  }
  return "default";
});

async function loadFollowStatus(): Promise<void> {
  if (!authStore.user.isLoggedIn || authStore.user.username === props.username) {
    return;
  }
  
  try {
    const response = await axios.get(getUrl(`follow/${props.username}/`));
    followStatus.value = response.data;
  } catch (error) {
    // Don't show error for follow status fetch
    console.log("Error loading follow status:", error);
  }
}

async function toggleFollow(): Promise<void> {
  if (!authStore.user.isLoggedIn) {
    $toast.error("Please log in to follow users");
    return;
  }
  
  followLoading.value = true;
  
  try {
    if (followStatus.value?.is_following) {
      // Unfollow
      const response = await axios.delete(getUrl(`follow/${props.username}/`));
      followStatus.value = {
        is_following: response.data.is_following,
        followers_count: response.data.followers_count,
        following_count: response.data.following_count,
      };
      $toast.success(`Unfollowed ${props.username}`);
    } else {
      // Follow
      const response = await axios.post(getUrl(`follow/${props.username}/`));
      followStatus.value = {
        is_following: response.data.is_following,
        followers_count: response.data.followers_count,
        following_count: response.data.following_count,
      };
      $toast.success(`Now following ${props.username}`);
    }
  } catch (error) {
    console.log(error);
    $toast.error("Error updating follow status");
  } finally {
    followLoading.value = false;
  }
}

onMounted(() => {
  loadFollowStatus();
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

.profile-text-info {
  flex: 1;
  min-width: 0;
}

.profile-text-info h2 {
  margin: 0 0 8px 0;
  color: white;
  font-size: 2rem;
  font-weight: 700;
}

.follow-stats {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  font-weight: 500;
}

.follow-stat-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: all 0.2s ease;
  border-radius: 4px;
  padding: 2px 4px;
}

.follow-stat-link:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
  text-decoration: none;
}

.profile-avatar {
  flex-shrink: 0;
}

.follow-button-wrapper {
  flex-shrink: 0;
}

.follow-btn-profile {
  min-width: 120px;
  font-weight: 600;
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
