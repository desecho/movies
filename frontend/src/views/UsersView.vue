<template>
  <v-container>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="page-header">
          <h1 class="page-title">
            <v-icon icon="mdi-account-group" class="title-icon" />
            Users
          </h1>
          <p class="page-subtitle">Browse movie collections from other users</p>
        </div>
      </v-col>
    </v-row>

    <!-- Users Grid -->
    <v-row>
      <v-col cols="12">
        <div v-if="loading" class="loading-container">
          <v-progress-circular indeterminate color="primary" size="50" />
          <p class="loading-text">Loading users...</p>
        </div>

        <div v-else-if="users.length === 0" class="empty-state">
          <v-icon icon="mdi-account-off" class="empty-icon" />
          <h3>No users found</h3>
          <p>There are no other users to display at the moment.</p>
        </div>

        <div v-else class="users-grid">
          <div v-for="(user, index) in users" :key="index" class="user-card">
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
                  <p class="user-subtitle">View movie collection</p>
                  <div v-if="user.followersCount !== undefined" class="follow-stats">
                    {{ user.followersCount }} followers • {{ user.followingCount }} following
                  </div>
                </div>
                <div class="user-actions">
                  <v-icon icon="mdi-chevron-right" class="action-icon" />
                </div>
              </router-link>

              <!-- Follow Button -->
              <div
                v-if="authStore.user.isLoggedIn && authStore.user.username !== user.username"
                class="follow-button-container"
              >
                <v-btn
                  :loading="user.followLoading"
                  :color="user.isFollowing ? 'success' : 'primary'"
                  :variant="user.isFollowing ? 'outlined' : 'elevated'"
                  size="small"
                  class="follow-btn"
                  @click.stop="toggleFollow(user)"
                >
                  <v-icon :icon="user.isFollowing ? 'mdi-account-check' : 'mdi-account-plus'" start />
                  {{ user.isFollowing ? "Following" : "Follow" }}
                </v-btn>
              </div>
            </div>
          </div>
        </div>
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

interface User {
  username: string;
  avatar_url: string | null;
  isFollowing?: boolean;
  followersCount?: number;
  followingCount?: number;
  followLoading?: boolean;
}

const authStore = useAuthStore();
interface FollowStatusResponse {
  is_following: boolean;
  followers_count: number;
  following_count: number;
}

const users: Ref<User[]> = ref([]);
const loading = ref(true);

async function loadFollowStatuses(): Promise<void> {
  const followPromises = users.value.map(async (user) => {
    try {
      const response = await axios.get<FollowStatusResponse>(getUrl(`follow/${user.username}/`));
      const newUser = {
        ...user,
        isFollowing: response.data.is_following,
        followersCount: response.data.followers_count,
        followingCount: response.data.following_count,
        followLoading: false,
      };
      const index = users.value.findIndex((u) => u.username === user.username);
      if (index > -1) {
        users.value[index] = newUser;
      }
    } catch {
      // Ignore errors for follow status
      const newUser = {
        ...user,
        isFollowing: false,
        followLoading: false,
      };
      const index = users.value.findIndex((u) => u.username === user.username);
      if (index > -1) {
        users.value[index] = newUser;
      }
    }
  });

  await Promise.all(followPromises);
}

async function loadUsers(): Promise<void> {
  loading.value = true;
  try {
    const response = await axios.get(getUrl("users/"));
    users.value = response.data as User[];

    // Load follow status for each user if logged in
    if (authStore.user.isLoggedIn) {
      void loadFollowStatuses();
    }
  } catch (error: unknown) {
    console.log(error);
    $toast.error("Error loading users");
  } finally {
    loading.value = false;
  }
}

async function toggleFollow(user: User): Promise<void> {
  if (!authStore.user.isLoggedIn) {
    $toast.error("Please log in to follow users");
    return;
  }

  const index = users.value.findIndex((u) => u.username === user.username);
  if (index === -1) {
    return;
  }

  const updatedUser = { ...users.value[index], followLoading: true };
  users.value[index] = updatedUser;

  try {
    if (user.isFollowing) {
      // Unfollow
      const response = await axios.delete<FollowStatusResponse>(getUrl(`follow/${user.username}/`));
      users.value[index] = {
        ...users.value[index],
        isFollowing: response.data.is_following,
        followersCount: response.data.followers_count,
        followingCount: response.data.following_count,
        followLoading: false,
      };
      $toast.success(`Unfollowed ${user.username}`);
    } else {
      // Follow
      const response = await axios.post<FollowStatusResponse>(getUrl(`follow/${user.username}/`));
      users.value[index] = {
        ...users.value[index],
        isFollowing: response.data.is_following,
        followersCount: response.data.followers_count,
        followingCount: response.data.following_count,
        followLoading: false,
      };
      $toast.success(`Now following ${user.username}`);
    }
  } catch (error: unknown) {
    console.log(error);
    users.value[index] = { ...users.value[index], followLoading: false };
    $toast.error("Error updating follow status");
  }
}

onMounted(() => {
  void loadUsers();
});
</script>

<style scoped>
/* Page Header Styling */
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
  margin: 0;
  opacity: 0.8;
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
  margin: 0 0 8px 0;
  color: #1f2937;
  line-height: 1.2;
  word-break: break-word;
}

.user-subtitle {
  font-size: 0.95rem;
  color: #6b7280;
  margin: 0 0 4px 0;
  font-weight: 500;
}

.follow-stats {
  font-size: 0.85rem;
  color: #9ca3af;
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

/* Follow Button */
.follow-button-container {
  display: flex;
  align-items: center;
  margin-left: 16px;
}

.follow-btn {
  min-width: 100px;
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

  .user-subtitle {
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
