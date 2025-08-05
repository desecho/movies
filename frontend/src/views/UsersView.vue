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
            <router-link :to="`/users/${user.username}/list/watched`" class="user-link">
              <div class="user-card-content">
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
                </div>
                <div class="user-actions">
                  <v-icon icon="mdi-chevron-right" class="action-icon" />
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { onMounted, ref } from "vue";

import type { AxiosError } from "axios";
import type { Ref } from "vue";

import { getUrl } from "../helpers";
import { $toast } from "../toast";

interface User {
  username: string;
  avatar_url: string | null;
}

const users: Ref<User[]> = ref([]);
const loading = ref(true);

function loadUsers(): void {
  loading.value = true;
  axios
    .get(getUrl("users/"))
    .then((response) => {
      users.value = response.data as User[];
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Error loading users");
    })
    .finally(() => {
      loading.value = false;
    });
}

onMounted(() => {
  loadUsers();
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
  display: block;
  width: 100%;
  height: 100%;
}

.user-card-content {
  padding: 32px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
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
