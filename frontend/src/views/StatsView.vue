<template>
  <div class="stats-view">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Your Movie Stats</h1>
        <p class="page-subtitle">Insights into your movie watching journey</p>
      </div>
    </div>

    <v-container fluid>
      <div v-if="loading" class="text-center">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4">Loading your stats...</p>
      </div>

      <div v-else-if="error" class="text-center">
        <v-alert type="error" :text="error"></v-alert>
      </div>

      <div v-else class="stats-content">
        <!-- Overview Cards -->
        <v-row class="mb-6">
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card text-center">
              <v-card-text>
                <v-icon size="48" color="success" class="mb-3">mdi-eye</v-icon>
                <h2 class="text-h4 font-weight-bold">{{ stats.totalMoviesWatched }}</h2>
                <p class="text-subtitle-1">Movies Watched</p>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card text-center">
              <v-card-text>
                <v-icon size="48" color="warning" class="mb-3">mdi-eye-off</v-icon>
                <h2 class="text-h4 font-weight-bold">{{ stats.totalMoviesToWatch }}</h2>
                <p class="text-subtitle-1">To Watch</p>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card text-center">
              <v-card-text>
                <v-icon size="48" color="info" class="mb-3">mdi-clock</v-icon>
                <h2 class="text-h4 font-weight-bold">{{ stats.totalHoursWatched }}</h2>
                <p class="text-subtitle-1">Hours Watched</p>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card text-center">
              <v-card-text>
                <v-icon size="48" color="primary" class="mb-3">mdi-star</v-icon>
                <h2 class="text-h4 font-weight-bold">
                  {{ stats.averageRating ? stats.averageRating : "N/A" }}
                </h2>
                <p class="text-subtitle-1">Average Rating</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Charts and Details -->
        <v-row>
          <!-- Quality Preferences -->
          <v-col cols="12" md="6">
            <v-card class="stat-card">
              <v-card-title>
                <v-icon class="mr-2">mdi-quality-high</v-icon>
                Quality Preferences
              </v-card-title>
              <v-card-text>
                <div v-for="(value, key) in stats.qualityPreferences" :key="key" class="quality-item">
                  <div class="d-flex justify-space-between align-center mb-2">
                    <span class="text-capitalize">{{ formatQualityLabel(key) }}</span>
                    <v-chip size="small" color="primary">{{ value }}</v-chip>
                  </div>
                  <v-progress-linear
                    :model-value="getQualityPercentage(value)"
                    color="primary"
                    height="6"
                    class="mb-3"
                  ></v-progress-linear>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Top Genres -->
          <v-col cols="12" md="6">
            <v-card class="stat-card">
              <v-card-title>
                <v-icon class="mr-2">mdi-tag</v-icon>
                Top Genres
              </v-card-title>
              <v-card-text>
                <div v-if="stats.topGenres.length === 0" class="text-center">
                  <p class="text-muted">No genre data available</p>
                </div>
                <div v-else>
                  <div v-for="genre in stats.topGenres" :key="genre.name" class="genre-item">
                    <div class="d-flex justify-space-between align-center mb-2">
                      <span>{{ genre.name }}</span>
                      <v-chip size="small" color="success">{{ genre.count }}</v-chip>
                    </div>
                    <v-progress-linear
                      :model-value="getGenrePercentage(genre.count)"
                      color="success"
                      height="6"
                      class="mb-3"
                    ></v-progress-linear>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Top Directors -->
          <v-col cols="12" md="6">
            <v-card class="stat-card">
              <v-card-title>
                <v-icon class="mr-2">mdi-movie-open</v-icon>
                Top Directors
              </v-card-title>
              <v-card-text>
                <div v-if="stats.topDirectors.length === 0" class="text-center">
                  <p class="text-muted">No director data available</p>
                </div>
                <div v-else>
                  <div v-for="director in stats.topDirectors" :key="director.name" class="director-item">
                    <div class="d-flex justify-space-between align-center mb-2">
                      <span>{{ director.name }}</span>
                      <v-chip size="small" color="warning">{{ director.count }}</v-chip>
                    </div>
                    <v-progress-linear
                      :model-value="getDirectorPercentage(director.count)"
                      color="warning"
                      height="6"
                      class="mb-3"
                    ></v-progress-linear>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Top Actors -->
          <v-col cols="12" md="6">
            <v-card class="stat-card">
              <v-card-title>
                <v-icon class="mr-2">mdi-account-star</v-icon>
                Top Actors
              </v-card-title>
              <v-card-text>
                <div v-if="stats.topActors.length === 0" class="text-center">
                  <p class="text-muted">No actor data available</p>
                </div>
                <div v-else>
                  <div v-for="actor in stats.topActors" :key="actor.name" class="actor-item">
                    <div class="d-flex justify-space-between align-center mb-2">
                      <span>{{ actor.name }}</span>
                      <v-chip size="small" color="error">{{ actor.count }}</v-chip>
                    </div>
                    <v-progress-linear
                      :model-value="getActorPercentage(actor.count)"
                      color="error"
                      height="6"
                      class="mb-3"
                    ></v-progress-linear>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Rating Distribution -->
          <v-col cols="12" md="6">
            <v-card class="stat-card">
              <v-card-title>
                <v-icon class="mr-2">mdi-star-box</v-icon>
                Rating Distribution
              </v-card-title>
              <v-card-text>
                <div v-if="Object.keys(stats.ratingDistribution).length === 0" class="text-center">
                  <p class="text-muted">No rating data available</p>
                </div>
                <div v-else>
                  <div v-for="(count, rating) in stats.ratingDistribution" :key="rating" class="rating-item">
                    <div class="d-flex justify-space-between align-center mb-2">
                      <div class="d-flex align-center">
                        <span class="mr-2">{{ rating }}</span>
                        <v-icon size="16" color="amber">mdi-star</v-icon>
                      </div>
                      <v-chip size="small" color="info">{{ count }}</v-chip>
                    </div>
                    <v-progress-linear
                      :model-value="getRatingPercentage(count)"
                      color="info"
                      height="6"
                      class="mb-3"
                    ></v-progress-linear>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Monthly Trends -->
        <v-row>
          <v-col cols="12">
            <v-card class="stat-card">
              <v-card-title>
                <v-icon class="mr-2">mdi-trending-up</v-icon>
                Monthly Watching Trends (Last 12 Months)
              </v-card-title>
              <v-card-text>
                <div class="monthly-trends">
                  <div v-for="month in stats.monthlyTrends" :key="month.month" class="trend-item">
                    <div class="trend-header">
                      <span class="trend-month">{{ formatMonth(month.month) }}</span>
                      <v-chip size="small" color="secondary">{{ month.count }}</v-chip>
                    </div>
                    <v-progress-linear
                      :model-value="getTrendPercentage(month.count)"
                      color="secondary"
                      height="8"
                      class="mt-1"
                    ></v-progress-linear>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-container>
  </div>
</template>

<script lang="ts" setup>
import axios from "axios";
import { onMounted, ref } from "vue";

import { getUrl } from "../helpers";

interface QualityPreferences {
  theatre: number;
  hd: number;
  fullHd: number;
  fourK: number;
  extended: number;
  original: number;
}

interface TopItem {
  name: string;
  count: number;
}

interface MonthlyTrend {
  month: string;
  count: number;
}

interface Stats {
  totalMoviesWatched: number;
  totalMoviesToWatch: number;
  totalHoursWatched: number;
  averageRating: number | null;
  totalRatedMovies: number;
  qualityPreferences: QualityPreferences;
  topGenres: TopItem[];
  topDirectors: TopItem[];
  topActors: TopItem[];
  monthlyTrends: MonthlyTrend[];
  ratingDistribution: Record<string, number>;
}

const loading = ref(true);
const error = ref<string | null>(null);
const stats = ref<Stats>({
  totalMoviesWatched: 0,
  totalMoviesToWatch: 0,
  totalHoursWatched: 0,
  averageRating: null,
  totalRatedMovies: 0,
  qualityPreferences: {
    theatre: 0,
    hd: 0,
    fullHd: 0,
    fourK: 0,
    extended: 0,
    original: 0,
  },
  topGenres: [],
  topDirectors: [],
  topActors: [],
  monthlyTrends: [],
  ratingDistribution: {},
});

async function loadStats(): Promise<void> {
  try {
    loading.value = true;
    const response = await axios.get(getUrl("stats/"));
    stats.value = response.data as Stats;
  } catch (err) {
    error.value = "Failed to load statistics. Please try again later.";
    console.error("Error loading stats:", err);
  } finally {
    loading.value = false;
  }
}

function formatQualityLabel(key: string): string {
  const labels: Record<string, string> = {
    theatre: "Theatre",
    hd: "HD",
    fullHd: "Full HD",
    fourK: "4K",
    extended: "Extended Cut",
    original: "Original Version",
  };
  return labels[key] || key;
}

function getQualityPercentage(value: number): number {
  const total = stats.value.totalMoviesWatched;
  return total > 0 ? (value / total) * 100 : 0;
}

function getGenrePercentage(count: number): number {
  const maxCount = stats.value.topGenres[0]?.count || 1;
  return (count / maxCount) * 100;
}

function getDirectorPercentage(count: number): number {
  const maxCount = stats.value.topDirectors[0]?.count || 1;
  return (count / maxCount) * 100;
}

function getActorPercentage(count: number): number {
  const maxCount = stats.value.topActors[0]?.count || 1;
  return (count / maxCount) * 100;
}

function getRatingPercentage(count: number): number {
  const maxCount = Math.max(...Object.values(stats.value.ratingDistribution));
  return (count / maxCount) * 100;
}

function getTrendPercentage(count: number): number {
  const maxCount = Math.max(...stats.value.monthlyTrends.map((t) => t.count));
  return maxCount > 0 ? (count / maxCount) * 100 : 0;
}

function formatMonth(monthStr: string): string {
  const [year, month] = monthStr.split("-");
  const date = new Date(parseInt(year, 10), parseInt(month, 10) - 1);
  return date.toLocaleDateString("en-US", { month: "short", year: "numeric" });
}

onMounted(() => {
  void loadStats();
});
</script>

<style scoped>
.stats-view {
  min-height: 100vh;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 0;
  margin-bottom: 2rem;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.page-subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0;
}

.stats-content {
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  height: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.quality-item,
.genre-item,
.director-item,
.actor-item,
.rating-item {
  margin-bottom: 1rem;
}

.monthly-trends {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.trend-item {
  padding: 0.5rem;
  border-radius: 8px;
  background: rgba(var(--v-theme-surface-variant), 0.1);
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.trend-month {
  font-size: 0.875rem;
  font-weight: 500;
}

.text-muted {
  color: rgba(var(--v-theme-on-surface), 0.6);
}

/* Dark theme adjustments */
.dark-theme .stat-card {
  background: var(--background-card);
  border: 1px solid var(--border-color);
}

.dark-theme .trend-item {
  background: rgba(102, 126, 234, 0.1);
}

.dark-theme .text-muted {
  color: var(--text-secondary);
}
</style>
