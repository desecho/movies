<template>
  <v-container>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="page-header">
          <h1 class="page-title">
            <v-icon icon="mdi-account-network" class="title-icon" />
            My Network
          </h1>
          <p class="page-subtitle">Manage your following and followers</p>
        </div>
      </v-col>
    </v-row>

    <!-- Network Tabs -->
    <v-row>
      <v-col cols="12">
        <v-tabs v-model="activeTab" class="network-tabs" grow>
          <v-tab value="following" class="network-tab">
            <v-icon icon="mdi-account-heart" class="tab-icon" />
            Following
            <v-chip v-if="followingUsers.length > 0" size="small" class="ml-2">
              {{ followingUsers.length }}
            </v-chip>
          </v-tab>
          <v-tab value="followers" class="network-tab">
            <v-icon icon="mdi-account-group" class="tab-icon" />
            Followers
            <v-chip v-if="followers.length > 0" size="small" class="ml-2">
              {{ followers.length }}
            </v-chip>
          </v-tab>
        </v-tabs>

        <v-tabs-window v-model="activeTab" class="network-tabs-window">
          <!-- Following Tab -->
          <v-tabs-window-item value="following">
            <!-- Loading State -->
            <div v-if="followingLoading" class="loading-container">
              <v-progress-circular indeterminate color="primary" size="50" />
              <p class="loading-text">Loading following list...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="followingUsers.length === 0" class="empty-state">
              <v-icon icon="mdi-account-heart-outline" class="empty-icon" />
              <h3>You're not following anyone yet</h3>
              <p>Start following users to see their movie activity in your feed.</p>
              <v-btn color="primary" variant="elevated" to="/users" class="mt-4">
                <v-icon icon="mdi-account-group" start />
                Browse Users
              </v-btn>
            </div>

            <!-- Following List -->
            <div v-else class="users-section">
              <div class="users-grid">
                <div v-for="(user, index) in followingUsers" :key="index" class="user-card">
                  <div class="user-card-content">
                    <router-link :to="`/users/${user.username}/list/watched`" class="user-link">
                      <div class="user-avatar">
                        <img
                          v-if="user.avatar_url"
                          :src="user.avatar_url"
                          :alt="`${user.username}'s avatar`"
                          class="avatar-image"
                        />
                        <v-icon v-else icon="mdi-account-circle" class="avatar-icon" />
                      </div>
                      <div class="user-info">
                        <h3 class="username">{{ user.username }}</h3>
                        <p class="follow-date">Following since {{ formatDate(user.follow_date) }}</p>
                      </div>
                      <div class="user-actions">
                        <v-icon icon="mdi-chevron-right" class="action-icon" />
                      </div>
                    </router-link>

                    <!-- Unfollow Button -->
                    <div class="action-button-container">
                      <v-btn
                        :loading="user.unfollowLoading"
                        color="success"
                        variant="outlined"
                        size="small"
                        class="action-btn"
                        @click.stop="unfollowUser(user)"
                      >
                        <v-icon icon="mdi-account-check" start />
                        Following
                      </v-btn>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </v-tabs-window-item>

          <!-- Followers Tab -->
          <v-tabs-window-item value="followers">
            <!-- Loading State -->
            <div v-if="followersLoading" class="loading-container">
              <v-progress-circular indeterminate color="primary" size="50" />
              <p class="loading-text">Loading followers...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="followers.length === 0" class="empty-state">
              <v-icon icon="mdi-account-group-outline" class="empty-icon" />
              <h3>No followers yet</h3>
              <p>When other users follow you, they'll appear here.</p>
              <v-btn color="primary" variant="elevated" to="/users" class="mt-4">
                <v-icon icon="mdi-account-group" start />
                Browse Users
              </v-btn>
            </div>

            <!-- Followers List -->
            <div v-else class="users-section">
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

                    <!-- Follow Back Button -->
                    <div class="action-button-container">
                      <v-btn
                        v-if="!follower.isFollowingBack"
                        :loading="follower.followLoading"
                        color="primary"
                        variant="elevated"
                        size="small"
                        class="action-btn"
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
                        class="action-btn"
                        @click.stop="unfollowFollower(follower)"
                      >
                        <v-icon icon="mdi-account-check" start />
                        Following
                      </v-btn>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { onMounted, ref } from "vue";

import type { Ref } from "vue";

import { getUrl } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";

interface FollowingUser {
  username: string;
  avatar_url: string | null;
  follow_date: string;
  unfollowLoading?: boolean;
}

interface Follower {
  username: string;
  avatar_url: string | null;
  follow_date: string;
  isFollowingBack?: boolean;
  followLoading?: boolean;
}

interface FollowingResponse {
  count: number;
  results: FollowingUser[];
}

interface FollowersResponse {
  count: number;
  results: Follower[];
}

interface FollowStatusResponse {
  is_following: boolean;
}

const authStore = useAuthStore();
const activeTab = ref("following");

// Following state
const followingUsers: Ref<FollowingUser[]> = ref([]);
const followingLoading = ref(true);

// Followers state
const followers: Ref<Follower[]> = ref([]);
const followersLoading = ref(true);

// Check follow back statuses function
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

// Following functions
async function loadFollowingUsers(): Promise<void> {
  if (!authStore.user.isLoggedIn) {
    $toast.error("Please log in to view your network");
    return;
  }

  followingLoading.value = true;
  try {
    const response = await axios.get(getUrl("user/following/"));
    const data = response.data as FollowingResponse;

    followingUsers.value = data.results.map((user) => ({
      ...user,
      unfollowLoading: false,
    }));
  } catch (error) {
    console.error("Error loading following list:", error);
    $toast.error("Error loading following list");
  } finally {
    followingLoading.value = false;
  }
}

async function unfollowUser(user: FollowingUser): Promise<void> {
  user.unfollowLoading = true;

  try {
    await axios.delete(getUrl(`follow/${user.username}/`));

    // Remove user from the list
    const index = followingUsers.value.findIndex((u) => u.username === user.username);
    if (index > -1) {
      followingUsers.value.splice(index, 1);
    }

    $toast.success(`Unfollowed ${user.username}`);
  } catch (error) {
    console.error("Error unfollowing user:", error);
    $toast.error("Error unfollowing user");
  } finally {
    user.unfollowLoading = false;
  }
}

// Followers functions
async function loadFollowers(): Promise<void> {
  if (!authStore.user.isLoggedIn) {
    $toast.error("Please log in to view your network");
    return;
  }

  followersLoading.value = true;
  try {
    const response = await axios.get(getUrl("user/followers/"));
    const data = response.data as FollowersResponse;

    followers.value = data.results.map((follower) => ({
      ...follower,
      followLoading: false,
      isFollowingBack: false,
    }));

    // Check which followers we're following back
    void checkFollowBackStatuses();
  } catch (error) {
    console.error("Error loading followers:", error);
    $toast.error("Error loading followers");
  } finally {
    followersLoading.value = false;
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

async function unfollowFollower(follower: Follower): Promise<void> {
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
  void loadFollowingUsers();
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

/* Network Tabs */
.network-tabs {
  margin-bottom: 32px;
}

.network-tab {
  font-weight: 600;
  font-size: 1rem;
}

.tab-icon {
  margin-right: 8px;
}

.network-tabs-window {
  min-height: 400px;
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

/* Users Section */
.users-section {
  padding: 24px 0;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
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

/* Action Button */
.action-button-container {
  display: flex;
  align-items: center;
  margin-left: 16px;
  flex-shrink: 0;
}

.action-btn {
  min-width: 110px;
  font-weight: 600;
  white-space: nowrap;
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
  }

  .user-card-content {
    padding: 24px 20px;
    min-height: 100px;
    gap: 16px;
    flex-wrap: wrap;
  }

  .action-button-container {
    margin-left: 0;
    margin-top: 8px;
    width: 100%;
    justify-content: flex-end;
  }

  .action-btn {
    min-width: 100px;
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

  .network-tab {
    font-size: 0.9rem;
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
    flex-wrap: wrap;
  }

  .action-button-container {
    margin-left: 0;
    margin-top: 8px;
    width: 100%;
    justify-content: flex-end;
  }

  .action-btn {
    min-width: 90px;
    font-size: 0.8rem;
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
