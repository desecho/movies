<template>
  <UserListView
    :username="username"
    :is-public-view="isPublicView"
    :config="followingConfig"
    @users-loaded="onUsersLoaded"
  >
    <template #action-button="{ user }">
      <v-btn
        :loading="user.unfollowLoading"
        color="success"
        variant="outlined"
        size="small"
        class="unfollow-btn"
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
import { $toast } from "../toast";

interface Props {
  username?: string;
  isPublicView?: boolean;
}

const props = defineProps<Props>();

interface FollowingUser {
  username: string;
  avatar_url: string | null;
  follow_date: string;
  unfollowLoading?: boolean;
}

const followingUsers: Ref<FollowingUser[]> = ref([]);

const followingConfig = {
  icon: "mdi-account-heart",
  title: "Following",
  publicSubtitle: `People ${props.username} is following`,
  personalSubtitle: "People you're following",
  loadingText: "Loading following list...",
  emptyIcon: "mdi-account-heart-outline",
  emptyTitle: props.isPublicView ? "Not following anyone yet" : "You're not following anyone yet",
  publicEmptyText: `${props.username} isn't following anyone yet.`,
  personalEmptyText: "Start following users to see their movie activity in your feed.",
  statsText: "following",
  apiEndpoint: "following/",
  personalApiEndpoint: "user/following/",
  showActionButton: true,
};

function onUsersLoaded(users: FollowingUser[]): void {
  followingUsers.value = users.map((user) => ({
    ...user,
    unfollowLoading: false,
  }));
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
</script>

<style scoped>
.unfollow-btn {
  min-width: 100px;
  font-weight: 600;
}
</style>
