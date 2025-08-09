<template>
  <UserListView
    :username="username"
    :is-public-view="isPublicView"
    :config="followersConfig"
    @users-loaded="onUsersLoaded"
  >
    <template #action-button="{ user }">
      <v-btn
        v-if="!user.isFollowingBack"
        :loading="user.followLoading"
        color="primary"
        variant="elevated"
        size="small"
        class="follow-btn"
        @click.stop="followBack(user)"
      >
        <v-icon icon="mdi-account-plus" start />
        Follow Back
      </v-btn>
      <v-btn
        v-else
        :loading="user.followLoading"
        color="success"
        variant="outlined"
        size="small"
        class="following-btn"
        @click.stop="unfollowUser(user)"
      >
        <v-icon icon="mdi-account-check" start />
        Following
      </v-btn>
    </template>
  </UserListView>
</template>

<script lang="ts" setup>
import axios from "axios";
import { ref } from "vue";

import type { Ref } from "vue";

import UserListView from "../components/UserListView.vue";
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

interface FollowStatusResponse {
  is_following: boolean;
}

const authStore = useAuthStore();
const followers: Ref<Follower[]> = ref([]);

const followersConfig = {
  icon: "mdi-account-group",
  title: "Followers",
  publicSubtitle: `People who follow ${props.username}`,
  personalSubtitle: "People who follow you",
  loadingText: "Loading followers...",
  emptyIcon: "mdi-account-group-outline",
  emptyTitle: "No followers yet",
  publicEmptyText: `${props.username} doesn't have any followers yet.`,
  personalEmptyText: "When other users follow you, they'll appear here.",
  statsText: "followers",
  apiEndpoint: "followers/",
  personalApiEndpoint: "user/followers/",
  showActionButton: true,
};

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

function onUsersLoaded(users: Follower[]): void {
  followers.value = users.map((user) => ({
    ...user,
    followLoading: false,
    isFollowingBack: false,
  }));

  if (!props.isPublicView && authStore.user.isLoggedIn) {
    void checkFollowBackStatuses();
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
</script>

<style scoped>
.follow-btn,
.following-btn {
  min-width: 110px;
  font-weight: 600;
}
</style>
