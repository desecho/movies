<template>
  <ErrorBoundary context="Activity Feed" fallback-message="Unable to load the activity feed">
    <v-container>
      <!-- Page Header -->
      <v-row class="mb-6">
        <v-col cols="12">
          <div class="page-header">
            <h1 class="page-title">
              <v-icon icon="mdi-timeline" class="title-icon" />
              Activity Feed
            </h1>
            <p class="page-subtitle">See what movies your friends are watching and rating</p>
          </div>
        </v-col>
      </v-row>

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <v-progress-circular indeterminate color="primary" size="50" />
        <p class="loading-text">Loading feed...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="feedItems.length === 0" class="empty-state">
        <v-icon icon="mdi-timeline-clock-outline" class="empty-icon" />
        <h3>No activity yet</h3>
        <p>Follow some users to see their movie activity, or check back later!</p>
        <v-btn color="primary" variant="elevated" to="/users" class="mt-4">
          <v-icon icon="mdi-account-group" start />
          Browse Users
        </v-btn>
      </div>

      <!-- Feed Items -->
      <div v-else class="feed-container">
        <div v-for="item in feedItems" :key="item.id" class="feed-item">
          <div class="feed-item-content">
            <!-- User Avatar -->
            <div class="user-avatar">
              <img
                v-if="item.user.avatar_url"
                :src="item.user.avatar_url"
                :alt="`${item.user.username}'s avatar`"
                class="avatar-image"
              />
              <v-icon v-else icon="mdi-account-circle" class="avatar-icon" />
            </div>

            <!-- Activity Content -->
            <div class="activity-content">
              <!-- Activity Header -->
              <div class="activity-header">
                <span class="username">{{ item.user.username }}</span>
                <span class="activity-text">{{ getActivityText(item) }}</span>
                <span class="activity-time">{{ formatDate(item.date) }}</span>
              </div>

              <!-- Movie Info -->
              <div class="movie-info">
                <div class="movie-poster">
                  <img
                    v-if="item.movie.poster_small"
                    :src="item.movie.poster_small"
                    :alt="`${item.movie.title} poster`"
                    class="poster-image"
                  />
                  <div v-else class="poster-placeholder">
                    <v-icon icon="mdi-movie" />
                  </div>
                </div>

                <div class="movie-details">
                  <h4 class="movie-title">{{ item.movie.title }}</h4>
                  <p v-if="item.movie.release_date" class="movie-year">{{ item.movie.release_date }}</p>

                  <!-- Additional content based on action type -->
                  <div v-if="item.rating" class="rating-display">
                    <v-icon icon="mdi-star" class="star-icon" />
                    <span class="rating-text">{{ item.rating }}/10</span>
                  </div>

                  <div v-if="item.comment" class="comment-display">
                    <v-icon icon="mdi-comment-text" class="comment-icon" />
                    <span class="comment-text">"{{ item.comment }}"</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="hasMore" class="load-more-container">
          <v-btn :loading="loadingMore" color="primary" variant="outlined" class="load-more-btn" @click="loadMore">
            Load More
          </v-btn>
        </div>
      </div>
    </v-container>
  </ErrorBoundary>
</template>

<script lang="ts" setup>
import axios from "axios";
import { onMounted, ref } from "vue";

import type { AxiosError } from "axios";
import type { Ref } from "vue";

import ErrorBoundary from "../components/ErrorBoundary.vue";
import { getUrl } from "../helpers";
import { $toast } from "../toast";

interface FeedUser {
  username: string;
  avatar_url: string | null;
}

interface FeedMovie {
  id: number;
  title: string;
  poster_small: string | null;
  release_date: string | null;
  tmdb_id: number;
}

interface FeedAction {
  id: number;
  name: string;
}

interface FeedList {
  id: number;
  name: string;
}

interface FeedItem {
  id: number;
  user: FeedUser;
  action: FeedAction;
  movie: FeedMovie;
  date: string;
  list?: FeedList;
  rating?: number;
  comment?: string;
}

interface FeedResponse {
  results: FeedItem[];
  next: string | null;
}

const feedItems: Ref<FeedItem[]> = ref([]);
const loading = ref(true);
const loadingMore = ref(false);
const hasMore = ref(false);
const nextPage: Ref<string | null> = ref(null);

function loadFeed(url = getUrl("feed/")): void {
  const isLoadingMore = url !== getUrl("feed/");

  if (isLoadingMore) {
    loadingMore.value = true;
  } else {
    loading.value = true;
    feedItems.value = [];
  }

  axios
    .get(url)
    .then((response) => {
      const data = response.data as FeedResponse;

      if (isLoadingMore) {
        feedItems.value.push(...data.results);
      } else {
        feedItems.value = data.results;
      }

      hasMore.value = Boolean(data.next);
      nextPage.value = data.next;
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Error loading feed");
    })
    .finally(() => {
      loading.value = false;
      loadingMore.value = false;
    });
}

function loadMore(): void {
  if (nextPage.value && !loadingMore.value) {
    loadFeed(nextPage.value);
  }
}

function getActivityText(item: FeedItem): string {
  switch (item.action.name) {
    case "added to list":
      return item.list ? `added to ${item.list.name.toLowerCase()}` : "added to a list";
    case "list changed to":
      return item.list ? `moved to ${item.list.name.toLowerCase()}` : "changed list";
    case "added rating":
      return "rated";
    case "added comment":
      return "commented on";
    default:
      return "interacted with";
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (minutes < 60) {
    return `${minutes}m ago`;
  } else if (hours < 24) {
    return `${hours}h ago`;
  } else if (days < 7) {
    return `${days}d ago`;
  }
  return date.toLocaleDateString();
}

onMounted(() => {
  loadFeed();
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
  color: rgb(var(--v-theme-on-surface-variant));
  font-weight: 500;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: rgb(var(--v-theme-on-surface-variant));
}

.empty-icon {
  font-size: 4rem;
  color: rgba(var(--v-theme-on-surface), 0.3);
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin: 0 0 12px 0;
  color: rgb(var(--v-theme-on-surface));
}

.empty-state p {
  font-size: 1rem;
  margin: 0;
  color: rgb(var(--v-theme-on-surface-variant));
  opacity: 0.8;
}

/* Feed Container */
.feed-container {
  max-width: 800px;
  margin: 0 auto;
}

.feed-item {
  background: rgb(var(--v-theme-surface));
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.feed-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.feed-item-content {
  padding: 24px;
  display: flex;
  gap: 16px;
}

/* User Avatar */
.user-avatar {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.avatar-icon {
  font-size: 2rem;
  color: white;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

/* Activity Content */
.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-header {
  margin-bottom: 16px;
  line-height: 1.4;
}

.username {
  font-weight: 700;
  color: rgb(var(--v-theme-on-surface));
  margin-right: 8px;
}

.activity-text {
  color: rgb(var(--v-theme-on-surface-variant));
  margin-right: 12px;
}

.activity-time {
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-size: 0.875rem;
  font-weight: 500;
}

/* Movie Info */
.movie-info {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.movie-poster {
  flex-shrink: 0;
  width: 60px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.poster-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  background: rgb(var(--v-theme-surface-variant));
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgb(var(--v-theme-on-surface-variant));
}

.movie-details {
  flex: 1;
  min-width: 0;
}

.movie-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: rgb(var(--v-theme-on-surface));
  margin: 0 0 4px 0;
  line-height: 1.3;
}

.movie-year {
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 0.875rem;
  margin: 0 0 12px 0;
}

/* Rating Display */
.rating-display {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.star-icon {
  color: #fbbf24;
  font-size: 1.125rem;
}

.rating-text {
  font-weight: 600;
  color: rgb(var(--v-theme-on-surface));
}

/* Comment Display */
.comment-display {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 8px;
  padding: 12px;
  background: rgb(var(--v-theme-surface-bright));
  border-radius: 8px;
  border-left: 3px solid rgb(var(--v-theme-primary));
}

.comment-icon {
  color: rgb(var(--v-theme-primary));
  font-size: 1rem;
  margin-top: 2px;
  flex-shrink: 0;
}

.comment-text {
  color: rgb(var(--v-theme-on-surface));
  font-style: italic;
  line-height: 1.4;
}

/* Load More */
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.load-more-btn {
  min-width: 140px;
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

  .feed-item-content {
    padding: 20px;
    gap: 12px;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
  }

  .avatar-icon {
    font-size: 1.5rem;
  }

  .movie-poster {
    width: 50px;
    height: 75px;
  }

  .movie-info {
    gap: 12px;
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

  .feed-item-content {
    padding: 16px;
    flex-direction: column;
    gap: 16px;
  }

  .user-avatar {
    align-self: flex-start;
  }

  .movie-info {
    gap: 16px;
  }
}
</style>
