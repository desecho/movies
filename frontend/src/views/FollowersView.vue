<template>
  <v-container>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="page-header">
          <h1 class="page-title">
            <v-icon icon="mdi-account-group" class="title-icon" />
            {{ isPublicView ? `${username}'s Followers` : "Followers" }}
          </h1>
          <p class="page-subtitle">{{ isPublicView ? `People who follow ${username}` : "People who follow you" }}</p>
        </div>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="50" />
      <p class="loading-text">Loading followers...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="followers.length === 0" class="empty-state">
      <v-icon icon="mdi-account-group-outline" class="empty-icon" />
      <h3>{{ isPublicView ? "No followers yet" : "No followers yet" }}</h3>
      <p>
        {{
          isPublicView
            ? `${username} doesn't have any followers yet.`
            : "When other users follow you, they'll appear here."
        }}
      </p>
      <v-btn v-if="!isPublicView" color="primary" variant="elevated" to="/users" class="mt-4">
        <v-icon icon="mdi-account-group" start />
        Browse Users
      </v-btn>
    </div>

    <!-- Followers List -->
    <div v-else>
      <div class="stats-header">
        <h3>{{ followers.length }} followers</h3>
      </div>

      <div class="users-grid">
        <div v-for="(follower, index) in followers" :key="index" class="user-card">
          <div class="user-card-content">
            <router-link :to="`/users/${follower.username}/list/watched`" class="user-link">
              <div class="user-avatar">
                <img
                  v-if="follower.avatar_url"
                  :src="follower.avatar_url"
                  :alt="`${follower.username}'s avatar`"
                  class="avatar-image"
                />
                <v-icon v-else icon="mdi-account-circle" class="avatar-icon" />
              </div>
              <div class="user-info">
                <h3 class="username">{{ follower.username }}</h3>
                <p class="follow-date">Following since {{ formatDate(follower.follow_date) }}</p>
              </div>
              <div class="user-actions">
                <v-icon icon="mdi-chevron-right" class="action-icon" />
              </div>
            </router-link>

            <!-- Follow Back Button (only show for personal view) -->
            <div v-if="!isPublicView" class="follow-back-container">
              <v-btn
                v-if="!follower.isFollowingBack"
                :loading="follower.followLoading"
                color="primary"
                variant="elevated"
                size="small"
                class="follow-btn"
                @click.stop="followBack(follower)"
              >
                <v-icon icon="mdi-account-plus" start />
                Follow Back
              </v-btn>
              <v-btn
                v-else
                :loading="follower.followLoading"
                color="success"
                variant="outlined"
                size="small"
                class="following-btn"
                @click.stop="unfollowUser(follower)"
              >
                <v-icon icon="mdi-account-check" start />
                Following
              </v-btn>
            </div>
          </div>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { onMounted, ref } from "vue";

import type { Ref } from "vue";

import { getUrl } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";

interface Props {
  username?: string;
  isPublicView?: boolean;
}

const props = defineProps<Props>();

interface Follower {
  username: string;
  avatar_url: string | null;
  follow_date: string;
  isFollowingBack?: boolean;
  followLoading?: boolean;
}

interface FollowersResponse {
  count: number;
  results: Follower[];
}

interface FollowStatusResponse {
  is_following: boolean;
}

const authStore = useAuthStore();
const followers: Ref<Follower[]> = ref([]);
const loading = ref(true);

async function checkFollowBackStatuses(): Promise<void> {
  const statusPromises = followers.value.map(async (follower) => {
    try {
      const response = await axios.get<FollowStatusResponse>(getUrl(`follow/${follower.username}/`));
      const newFollower = { ...follower, isFollowingBack: response.data.is_following };
      const index = followers.value.findIndex((f) => f.username === follower.username);
      if (index > -1) {
        followers.value[index] = newFollower;
      }
    } catch (error) {
      console.log(`Error checking follow status for ${follower.username}:`, error);
      const newFollower = { ...follower, isFollowingBack: false };
      const index = followers.value.findIndex((f) => f.username === follower.username);
      if (index > -1) {
        followers.value[index] = newFollower;
      }
    }
  });

  await Promise.all(statusPromises);
}

async function loadFollowers(): Promise<void> {
  loading.value = true;
  try {
    let apiUrl: string;

    if (props.isPublicView && props.username) {
      // Load public followers list for specified user
      apiUrl = getUrl(`users/${props.username}/followers/`);
    } else {
      // Load personal followers list
      if (!authStore.user.isLoggedIn) {
        $toast.error("Please log in to view your followers");
        return;
      }
      apiUrl = getUrl("user/followers/");
    }

    const response = await axios.get(apiUrl);
    const data = response.data as FollowersResponse;

    followers.value = data.results.map((follower) => ({
      ...follower,
      followLoading: false,
      isFollowingBack: false, // We'll check this below
    }));

    // Check which followers we're following back (only for personal view)
    if (!props.isPublicView && authStore.user.isLoggedIn) {
      void checkFollowBackStatuses();
    }
  } catch (error) {
    console.error("Error loading followers:", error);
    $toast.error("Error loading followers");
  } finally {
    loading.value = false;
  }
}

async function followBack(follower: Follower): Promise<void> {
  const index = followers.value.findIndex((f) => f.username === follower.username);
  if (index === -1) {
    return;
  }

  const updatedFollower = { ...followers.value[index], followLoading: true };
  followers.value[index] = updatedFollower;

  try {
    await axios.post(getUrl(`follow/${follower.username}/`));
    followers.value[index] = { ...followers.value[index], isFollowingBack: true, followLoading: false };
    $toast.success(`Now following ${follower.username}`);
  } catch (error) {
    console.error("Error following user:", error);
    followers.value[index] = { ...followers.value[index], followLoading: false };
    $toast.error("Error following user");
  }
}

async function unfollowUser(follower: Follower): Promise<void> {
  const index = followers.value.findIndex((f) => f.username === follower.username);
  if (index === -1) {
    return;
  }

  const updatedFollower = { ...followers.value[index], followLoading: true };
  followers.value[index] = updatedFollower;

  try {
    await axios.delete(getUrl(`follow/${follower.username}/`));
    followers.value[index] = { ...followers.value[index], isFollowingBack: false, followLoading: false };
    $toast.success(`Unfollowed ${follower.username}`);
  } catch (error) {
    console.error("Error unfollowing user:", error);
    followers.value[index] = { ...followers.value[index], followLoading: false };
    $toast.error("Error unfollowing user");
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 1) {
    return "yesterday";
  } else if (diffDays < 7) {
    return `${diffDays} days ago`;
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks} ${weeks === 1 ? "week" : "weeks"} ago`;
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30);
    return `${months} ${months === 1 ? "month" : "months"} ago`;
  }
  return date.toLocaleDateString();
}

onMounted(() => {
  void loadFollowers();
});
</script>

<style scoped>
/* Page Header */
.page-header {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  color: white;
  margin-bottom: 40px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.title-icon {
  font-size: 3rem;
  color: rgba(255, 255, 255, 0.9);
}

.page-subtitle {
  font-size: 1.2rem;
  margin: 0;
  opacity: 0.9;
  font-weight: 400;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-text {
  margin-top: 20px;
  font-size: 1.1rem;
  color: #6b7280;
  font-weight: 500;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #6b7280;
}

.empty-icon {
  font-size: 4rem;
  color: #d1d5db;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin: 0 0 12px 0;
  color: #4b5563;
}

.empty-state p {
  font-size: 1rem;
  margin: 0 0 20px 0;
  opacity: 0.8;
}

/* Stats Header */
.stats-header {
  margin-bottom: 24px;
  text-align: center;
}

.stats-header h3 {
  font-size: 1.5rem;
  color: #1f2937;
  font-weight: 600;
}

/* Users Grid */
.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  padding: 20px 0;
}

/* User Card */
.user-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;

  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
    border-color: rgba(102, 126, 234, 0.2);
  }
}

.user-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  flex: 1;
  align-items: center;
  gap: 20px;
}

.user-card-content {
  padding: 32px 24px;
  display: flex;
  align-items: center;
  gap: 0px;
  min-height: 120px;
}

/* User Avatar */
.user-avatar {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.avatar-icon {
  font-size: 2.5rem;
  color: white;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

/* User Info */
.user-info {
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1f2937;
  line-height: 1.2;
  word-break: break-word;
}

.follow-date {
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0;
  font-weight: 500;
}

/* User Actions */
.user-actions {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-icon {
  font-size: 1.5rem;
  color: #667eea;
  transition: transform 0.2s ease;
}

.user-card:hover .user-actions {
  background: rgba(102, 126, 234, 0.15);
  transform: scale(1.1);
}

.user-card:hover .action-icon {
  transform: translateX(2px);
}

/* Follow Back Button */
.follow-back-container {
  display: flex;
  align-items: center;
  margin-left: 16px;
}

.follow-btn,
.following-btn {
  min-width: 110px;
  font-weight: 600;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 2.2rem;
    flex-direction: column;
    gap: 12px;
  }

  .title-icon {
    font-size: 2.5rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }

  .users-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px 0;
  }

  .user-card-content {
    padding: 24px 20px;
    min-height: 100px;
    gap: 16px;
  }

  .user-avatar {
    width: 50px;
    height: 50px;
  }

  .avatar-icon {
    font-size: 2rem;
  }

  .username {
    font-size: 1.2rem;
  }

  .follow-date {
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 30px 16px;
    margin-bottom: 30px;
  }

  .page-title {
    font-size: 1.8rem;
  }

  .title-icon {
    font-size: 2rem;
  }

  .user-card-content {
    padding: 20px 16px;
    gap: 12px;
  }

  .user-avatar {
    width: 45px;
    height: 45px;
  }

  .avatar-icon {
    font-size: 1.8rem;
  }

  .username {
    font-size: 1.1rem;
  }
}
</style>
