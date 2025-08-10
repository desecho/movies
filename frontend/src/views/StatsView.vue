<template>
  <ErrorBoundary context="Movie Statistics" fallback-message="Unable to load your statistics">
    <div class="stats-view">
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">Your Movie Stats</h1>
          <p class="page-subtitle">Insights into your movie watching journey</p>
        </div>
      </div>

      <v-container fluid>
        <!-- Loading Indicator -->
        <LoadingIndicator
          v-if="statsOperation.isLoading.value"
          :show="true"
          variant="overlay"
          message="Loading your statistics..."
        />
        <!-- Year Selector -->
        <div
          v-if="!statsOperation.isLoading.value && stats.availableYears && stats.availableYears.length > 0"
          class="mb-6"
        >
          <div class="d-flex justify-space-between align-center mb-4">
            <h2 class="text-h5 font-weight-bold">View Statistics</h2>
            <YearSelectorComponent
              :available-years="stats.availableYears"
              :current-year="selectedYear"
              @year-changed="handleYearChange"
            />
          </div>
        </div>

        <!-- Year in Review Section -->
        <div v-if="!statsOperation.isLoading.value && selectedYear && stats.yearlyOverview" class="mb-6">
          <v-card class="year-review-card">
            <v-card-title class="year-review-title">
              <v-icon class="mr-3" size="32" color="primary">mdi-calendar-star</v-icon>
              <div>
                <h2 class="text-h4 font-weight-bold">{{ selectedYear }} Year in Review</h2>
                <p class="text-subtitle-1 mb-0 mt-1">Your movie watching journey this year</p>
              </div>
            </v-card-title>

            <v-card-text>
              <!-- Year Overview Stats -->
              <v-row class="mb-4">
                <v-col cols="12" sm="6" md="3">
                  <div class="yearly-stat-item">
                    <v-icon size="40" color="success" class="mb-2">mdi-movie</v-icon>
                    <h3 class="text-h4 font-weight-bold">{{ stats.yearlyOverview.totalMoviesWatched }}</h3>
                    <p class="text-body-2">Movies Watched</p>
                    <div v-if="stats.yearlyOverview.yearOverYearChange !== 0" class="year-change">
                      <v-chip
                        :color="stats.yearlyOverview.yearOverYearChange > 0 ? 'success' : 'error'"
                        size="small"
                        variant="flat"
                      >
                        <v-icon size="14" class="mr-1">
                          {{ stats.yearlyOverview.yearOverYearChange > 0 ? "mdi-trending-up" : "mdi-trending-down" }}
                        </v-icon>
                        {{ Math.abs(stats.yearlyOverview.yearOverYearChangePercent) }}%
                      </v-chip>
                    </div>
                  </div>
                </v-col>

                <v-col cols="12" sm="6" md="3">
                  <div class="yearly-stat-item">
                    <v-icon size="40" color="info" class="mb-2">mdi-clock</v-icon>
                    <h3 class="text-h4 font-weight-bold">{{ stats.yearlyOverview.totalHoursWatched }}</h3>
                    <p class="text-body-2">Hours Watched</p>
                    <p class="text-caption text-muted">
                      {{ Math.round((stats.yearlyOverview.totalHoursWatched / 24) * 10) / 10 }} days of content
                    </p>
                  </div>
                </v-col>

                <v-col cols="12" sm="6" md="3">
                  <div class="yearly-stat-item">
                    <v-icon size="40" color="warning" class="mb-2">mdi-chart-line</v-icon>
                    <h3 class="text-h4 font-weight-bold">{{ getMonthName(stats.yearlyOverview.peakMonth) }}</h3>
                    <p class="text-body-2">Peak Month</p>
                    <p class="text-caption text-muted">{{ stats.yearlyOverview.peakMonthCount }} movies</p>
                  </div>
                </v-col>

                <v-col cols="12" sm="6" md="3">
                  <div class="yearly-stat-item">
                    <v-icon size="40" color="primary" class="mb-2">mdi-star</v-icon>
                    <h3 class="text-h4 font-weight-bold">
                      {{ stats.averageRating ? stats.averageRating : "N/A" }}
                    </h3>
                    <p class="text-body-2">Average Rating</p>
                  </div>
                </v-col>
              </v-row>

              <!-- Milestones -->
              <div v-if="stats.yearlyMilestones" class="milestones-section">
                <h3 class="text-h6 font-weight-bold mb-4">
                  <v-icon class="mr-2">mdi-trophy</v-icon>
                  Year Highlights
                </h3>

                <v-row>
                  <v-col v-if="stats.yearlyMilestones.firstMovie" cols="12" md="6">
                    <v-card variant="outlined" class="milestone-card">
                      <v-card-text>
                        <div class="d-flex align-center mb-2">
                          <v-icon color="green" class="mr-2">mdi-play</v-icon>
                          <span class="font-weight-medium">First Movie</span>
                        </div>
                        <p class="text-body-1 mb-1">{{ stats.yearlyMilestones.firstMovie.title }}</p>
                        <p class="text-caption text-muted">{{ stats.yearlyMilestones.firstMovie.date }}</p>
                      </v-card-text>
                    </v-card>
                  </v-col>

                  <v-col v-if="stats.yearlyMilestones.highestRatedMovie" cols="12" md="6">
                    <v-card variant="outlined" class="milestone-card">
                      <v-card-text>
                        <div class="d-flex align-center mb-2">
                          <v-icon color="amber" class="mr-2">mdi-star</v-icon>
                          <span class="font-weight-medium">Highest Rated</span>
                        </div>
                        <p class="text-body-1 mb-1">{{ stats.yearlyMilestones.highestRatedMovie.title }}</p>
                        <div class="d-flex align-center">
                          <v-rating
                            :model-value="stats.yearlyMilestones.highestRatedMovie.rating"
                            readonly
                            density="compact"
                            size="small"
                            color="amber"
                          />
                          <span class="ml-2 text-caption"
                            >{{ stats.yearlyMilestones.highestRatedMovie.rating }}/10</span
                          >
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>

                  <v-col v-if="stats.yearlyMilestones.longestMovie" cols="12" md="6">
                    <v-card variant="outlined" class="milestone-card">
                      <v-card-text>
                        <div class="d-flex align-center mb-2">
                          <v-icon color="purple" class="mr-2">mdi-timer</v-icon>
                          <span class="font-weight-medium">Longest Movie</span>
                        </div>
                        <p class="text-body-1 mb-1">{{ stats.yearlyMilestones.longestMovie.title }}</p>
                        <p class="text-caption text-muted">{{ stats.yearlyMilestones.longestMovie.runtime }}</p>
                      </v-card-text>
                    </v-card>
                  </v-col>

                  <v-col v-if="stats.yearlyMilestones.topGenre" cols="12" md="6">
                    <v-card variant="outlined" class="milestone-card">
                      <v-card-text>
                        <div class="d-flex align-center mb-2">
                          <v-icon color="teal" class="mr-2">mdi-tag</v-icon>
                          <span class="font-weight-medium">Top Genre</span>
                        </div>
                        <p class="text-body-1 mb-1">{{ stats.yearlyMilestones.topGenre.name }}</p>
                        <p class="text-caption text-muted">{{ stats.yearlyMilestones.topGenre.count }} movies</p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <div v-if="!statsOperation.isLoading.value" class="stats-content">
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

            <!-- Release Date Overview -->
            <v-col cols="12" md="6">
              <v-card class="stat-card">
                <v-card-title>
                  <v-icon class="mr-2">mdi-calendar-clock</v-icon>
                  Release Date Overview
                </v-card-title>
                <v-card-text>
                  <div v-if="!stats.oldestMovie && !stats.newestMovie" class="text-center">
                    <p class="text-muted">No release date data available</p>
                  </div>
                  <div v-else class="release-overview">
                    <div v-if="stats.averageReleaseYear" class="overview-item mb-4">
                      <div class="d-flex justify-space-between align-center mb-2">
                        <div class="d-flex align-center">
                          <v-icon size="20" color="primary" class="mr-2">mdi-calendar-star</v-icon>
                          <span class="font-weight-medium">Average Release Year</span>
                        </div>
                        <v-chip size="small" color="primary">{{ Math.round(stats.averageReleaseYear) }}</v-chip>
                      </div>
                    </div>

                    <div v-if="stats.oldestMovie" class="overview-item mb-3">
                      <div class="d-flex align-center mb-1">
                        <v-icon size="16" color="brown" class="mr-2">mdi-history</v-icon>
                        <span class="text-caption font-weight-medium">Oldest Movie</span>
                      </div>
                      <div class="ml-6">
                        <p class="text-body-2 mb-0">{{ stats.oldestMovie.title }}</p>
                        <p class="text-caption text-muted">{{ stats.oldestMovie.releaseYear }}</p>
                      </div>
                    </div>

                    <div v-if="stats.newestMovie" class="overview-item">
                      <div class="d-flex align-center mb-1">
                        <v-icon size="16" color="green" class="mr-2">mdi-new-box</v-icon>
                        <span class="text-caption font-weight-medium">Newest Movie</span>
                      </div>
                      <div class="ml-6">
                        <p class="text-body-2 mb-0">{{ stats.newestMovie.title }}</p>
                        <p class="text-caption text-muted">{{ stats.newestMovie.releaseYear }}</p>
                      </div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Decade Distribution -->
            <v-col cols="12" md="6">
              <v-card class="stat-card">
                <v-card-title>
                  <v-icon class="mr-2">mdi-calendar-range</v-icon>
                  Movies by Decade
                </v-card-title>
                <v-card-text>
                  <div v-if="Object.keys(stats.decadeDistribution).length === 0" class="text-center">
                    <p class="text-muted">No decade data available</p>
                  </div>
                  <div v-else>
                    <div v-for="[decade, count] in getSortedDecades()" :key="decade" class="decade-item">
                      <div class="d-flex justify-space-between align-center mb-2">
                        <span>{{ decade }}</span>
                        <v-chip size="small" color="deep-purple">{{ count }}</v-chip>
                      </div>
                      <v-progress-linear
                        :model-value="getDecadePercentage(count)"
                        color="deep-purple"
                        height="6"
                        class="mb-3"
                      ></v-progress-linear>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Vintage Preferences -->
            <v-col cols="12" md="6">
              <v-card class="stat-card">
                <v-card-title>
                  <v-icon class="mr-2">mdi-timeline-clock</v-icon>
                  Era Preferences
                </v-card-title>
                <v-card-text>
                  <div class="vintage-preferences">
                    <div v-for="(count, era) in stats.vintagePreferences" :key="era" class="vintage-item">
                      <div class="d-flex justify-space-between align-center mb-2">
                        <div class="d-flex align-center">
                          <span class="mr-2">{{ formatEraLabel(era) }}</span>
                          <span class="text-caption text-muted">{{ getEraRange(era) }}</span>
                        </div>
                        <v-chip size="small" color="teal">{{ count }}</v-chip>
                      </div>
                      <v-progress-linear
                        :model-value="getVintagePercentage(count)"
                        color="teal"
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
  </ErrorBoundary>
</template>

<script lang="ts" setup>
import axios from "axios";
import { onMounted, ref } from "vue";

import ErrorBoundary from "../components/ErrorBoundary.vue";
import LoadingIndicator from "../components/LoadingIndicator.vue";
import YearSelectorComponent from "../components/YearSelectorComponent.vue";
import { useApiCall } from "../composables/useAsyncOperation";
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

interface YearlyOverview {
  totalMoviesWatched: number;
  totalHoursWatched: number;
  yearOverYearChange: number;
  yearOverYearChangePercent: number;
  peakMonth: number;
  peakMonthCount: number;
  monthlyDistribution: { month: number; count: number }[];
}

interface MovieMilestone {
  title: string;
  date?: string;
  rating?: number;
  runtime?: string;
}

interface TopItemMilestone {
  name: string;
  count: number;
}

interface YearlyMilestones {
  firstMovie?: MovieMilestone;
  lastMovie?: MovieMilestone;
  highestRatedMovie?: MovieMilestone;
  longestMovie?: MovieMilestone;
  topGenre?: TopItemMilestone;
  topDirector?: TopItemMilestone;
  topActor?: TopItemMilestone;
}

interface ReleaseMovie {
  title: string;
  releaseDate: string;
  releaseYear: number;
}

interface ReleaseYearItem {
  year: number;
  count: number;
}

interface VintagePreferences {
  classic: number;
  retro: number;
  modern: number;
  recent: number;
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
  decadeDistribution: Record<string, number>;
  averageReleaseYear: number | null;
  oldestMovie: ReleaseMovie | null;
  newestMovie: ReleaseMovie | null;
  topReleaseYears: ReleaseYearItem[];
  vintagePreferences: VintagePreferences;
  yearlyOverview?: YearlyOverview;
  yearlyMilestones?: YearlyMilestones;
  availableYears?: number[];
  selectedYear?: number;
  isCurrentYear?: boolean;
}

const selectedYear = ref<number | null>(null);

// Error handling composable
const statsOperation = useApiCall("Load Statistics");

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
  decadeDistribution: {},
  averageReleaseYear: null,
  oldestMovie: null,
  newestMovie: null,
  topReleaseYears: [],
  vintagePreferences: {
    classic: 0,
    retro: 0,
    modern: 0,
    recent: 0,
  },
  availableYears: [],
});

async function loadStats(year?: number | null): Promise<void> {
  const url = year ? `stats/?year=${year}` : "stats/";

  const result = await statsOperation.execute(async () => {
    const response = await axios.get(getUrl(url));
    return response.data as Stats;
  });

  if (result.success && result.data) {
    stats.value = result.data;
    selectedYear.value = year || null;
  }
}

function handleYearChange(year: number | null): void {
  void loadStats(year);
}

function getMonthName(monthNumber: number): string {
  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  return months[monthNumber - 1] || "Unknown";
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

function getSortedDecades(): Array<[string, number]> {
  return Object.entries(stats.value.decadeDistribution).sort((a, b) => {
    const yearA = parseInt(a[0].replace("s", ""), 10);
    const yearB = parseInt(b[0].replace("s", ""), 10);
    return yearA - yearB;
  });
}

function getDecadePercentage(count: number): number {
  const values = Object.values(stats.value.decadeDistribution);
  if (values.length === 0) {
    return 0;
  }
  const maxCount = Math.max(...values);
  return maxCount > 0 ? (count / maxCount) * 100 : 0;
}

function getVintagePercentage(count: number): number {
  const total = stats.value.totalMoviesWatched;
  return total > 0 ? (count / total) * 100 : 0;
}

function formatEraLabel(era: string): string {
  const labels: Record<string, string> = {
    classic: "Classic",
    retro: "Retro",
    modern: "Modern",
    recent: "Recent",
  };
  return labels[era] || era;
}

function getEraRange(era: string): string {
  const ranges: Record<string, string> = {
    classic: "Pre-1980",
    retro: "1980-1999",
    modern: "2000-2009",
    recent: "2010+",
  };
  return ranges[era] || "";
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
.rating-item,
.decade-item,
.vintage-item {
  margin-bottom: 1rem;
}

.release-overview .overview-item {
  padding: 8px 0;
}

.release-overview .overview-item:last-child {
  padding-bottom: 0;
}

.vintage-preferences .vintage-item:last-child {
  margin-bottom: 0;
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

/* Year in Review Styles */
.year-review-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.year-review-title {
  padding: 24px 24px 0;
  color: white;
}

.yearly-stat-item {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.yearly-stat-item h3 {
  color: white;
  margin: 8px 0 4px;
}

.yearly-stat-item p {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
}

.year-change {
  margin-top: 8px;
}

.milestones-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.milestones-section h3 {
  color: white;
}

.milestone-card {
  height: 100%;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(5px);
}

.milestone-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.milestone-card .v-card-text {
  color: white;
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

.dark-theme .year-review-card {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
}

/* Light theme text muted override */
.text-muted {
  color: rgba(255, 255, 255, 0.7) !important;
}
</style>
