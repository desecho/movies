<template>
  <div class="movie-detail-view">
    <div class="container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <v-progress-circular indeterminate color="primary" size="64" class="loading-spinner" />
        <p class="loading-text">Loading movie details...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-container">
        <v-alert type="error" title="Error Loading Movie" :text="error" class="error-alert" />
        <v-btn color="primary" class="retry-btn" @click="fetchMovieDetails"> Try Again </v-btn>
      </div>

      <!-- Movie Details -->
      <div v-else-if="movieData" class="movie-detail">
        <div class="movie-header">
          <div class="poster-section">
            <div class="poster-container">
              <v-lazy-image
                v-if="movieData.movie.hasPoster"
                :src="movieData.movie.posterBig"
                :alt="movieData.movie.title"
                :title="movieData.movie.titleOriginal"
                class="movie-poster"
              />
              <div v-else class="no-poster">
                <v-icon icon="mdi-movie" size="80" color="grey" />
                <p>No Poster Available</p>
              </div>
            </div>
          </div>

          <div class="movie-info">
            <div class="title-section">
              <h1 class="movie-title">{{ movieData.movie.title }}</h1>
              <h2 v-if="movieData.movie.titleOriginal !== movieData.movie.title" class="original-title">
                {{ movieData.movie.titleOriginal }}
              </h2>
            </div>

            <!-- Add to List Buttons for Authenticated Users -->
            <div v-if="isLoggedIn && !userRecord" class="add-to-list-section">
              <v-btn
                v-if="movieData.movie.isReleased"
                color="primary"
                :disabled="addingToList"
                class="add-btn"
                @click="addToList(listWatchedId)"
              >
                <v-icon icon="mdi-eye" />
                Add to Watched
              </v-btn>
              <v-btn
                v-else
                disabled
                color="primary"
                variant="outlined"
                class="add-btn disabled-watched-btn"
                title="Cannot add unreleased movie to watched list"
              >
                <v-icon icon="mdi-eye-off-outline" />
                Not Yet Released
              </v-btn>
              <v-btn color="secondary" :disabled="addingToList" class="add-btn" @click="addToList(listToWatchId)">
                <v-icon icon="mdi-eye-off" />
                Add to To Watch
              </v-btn>
            </div>

            <!-- User's Record Status -->
            <div v-else-if="userRecord" class="user-record-section">
              <v-chip
                :color="userRecord.listId === listWatchedId ? 'success' : 'info'"
                variant="elevated"
                class="record-chip"
              >
                <v-icon :icon="userRecord.listId === listWatchedId ? 'mdi-eye' : 'mdi-eye-off'" />
                {{ userRecord.listId === listWatchedId ? "In Watched List" : "In To Watch List" }}
              </v-chip>

              <!-- Rating Display -->
              <div v-if="userRecord.listId === listWatchedId && userRecord.rating" class="rating-section">
                <star-rating :rating="userRecord.rating" :star-size="25" :show-rating="false" :read-only="true" />
                <span class="rating-text">Your Rating</span>
              </div>
            </div>

            <!-- Movie Metadata -->
            <div class="metadata-grid">
              <div v-if="movieData.movie.releaseDate" class="metadata-item">
                <span class="label">Release Date:</span>
                <span class="value">{{ movieData.movie.releaseDate }}</span>
              </div>
              <div v-if="movieData.movie.runtime" class="metadata-item">
                <span class="label">Runtime:</span>
                <span class="value">{{ movieData.movie.runtime }}</span>
              </div>
              <div v-if="movieData.movie.imdbRating" class="metadata-item">
                <span class="label">IMDb Rating:</span>
                <span class="value">{{ movieData.movie.imdbRating }}/10</span>
              </div>
              <div v-if="movieData.movie.country" class="metadata-item">
                <span class="label">Country:</span>
                <span class="value">{{ movieData.movie.country }}</span>
              </div>
              <div v-if="movieData.movie.director" class="metadata-item">
                <span class="label">Director:</span>
                <span class="value">{{ movieData.movie.director }}</span>
              </div>
              <div v-if="movieData.movie.writer" class="metadata-item">
                <span class="label">Writer:</span>
                <span class="value">{{ movieData.movie.writer }}</span>
              </div>
              <div v-if="movieData.movie.genre" class="metadata-item">
                <span class="label">Genre:</span>
                <span class="value">{{ movieData.movie.genre }}</span>
              </div>
              <div v-if="movieData.movie.actors" class="metadata-item">
                <span class="label">Actors:</span>
                <span class="value">{{ movieData.movie.actors }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Overview -->
        <div v-if="movieData.movie.overview" class="overview-section">
          <h3>Overview</h3>
          <p class="overview-text">{{ movieData.movie.overview }}</p>
        </div>

        <!-- External Links -->
        <div class="links-section">
          <h3>External Links</h3>
          <div class="links-grid">
            <a
              v-if="movieData.movie.homepage"
              :href="movieData.movie.homepage"
              target="_blank"
              class="external-link website-link"
            >
              <v-icon icon="mdi-web" />
              Official Website
              <v-icon icon="mdi-open-in-new" size="small" />
            </a>
            <a :href="movieData.movie.imdbUrl" target="_blank" class="external-link imdb-link">
              <span class="imdb-logo"></span>
              IMDb
              <v-icon icon="mdi-open-in-new" size="small" />
            </a>
            <a :href="movieData.movie.tmdbUrl" target="_blank" class="external-link tmdb-link">
              <span class="tmdb-logo"></span>
              TMDB
              <v-icon icon="mdi-open-in-new" size="small" />
            </a>
          </div>
        </div>

        <!-- Trailers -->
        <div v-if="movieData.movie.trailers.length > 0" class="trailers-section">
          <h3>Trailers</h3>
          <div class="trailers-grid">
            <a
              v-for="trailer in movieData.movie.trailers"
              :key="trailer.name"
              :href="trailer.url"
              target="_blank"
              class="trailer-link"
            >
              <v-icon icon="mdi-play" />
              {{ trailer.name }}
              <v-icon icon="mdi-open-in-new" size="small" />
            </a>
          </div>
        </div>

        <!-- Streaming Providers -->
        <div v-if="movieData.providerRecords.length > 0" class="providers-section">
          <h3>Stream On</h3>
          <div class="providers-grid">
            <a
              v-for="providerRecord in movieData.providerRecords"
              :key="providerRecord.provider.name"
              :href="providerRecord.tmdbWatchUrl"
              target="_blank"
              class="provider-link"
            >
              <v-lazy-image
                :src="providerRecord.provider.logo"
                :alt="providerRecord.provider.name"
                :title="providerRecord.provider.name"
                class="provider-logo"
              />
              <span class="provider-name">{{ providerRecord.provider.name }}</span>
              <v-icon icon="mdi-open-in-new" size="small" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import axios, { isAxiosError } from "axios";
import VLazyImage from "v-lazy-image";
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import StarRating from "vue-star-rating";

import type { Movie, ProviderRecord, RecordType } from "../types";

import { listToWatchId, listWatchedId } from "../const";
import { getUrl } from "../helpers";
import { useAuthStore } from "../stores/auth";

interface MovieDetailResponse {
  movie: Movie;
  providerRecords: ProviderRecord[];
  userRecord: RecordType | null;
}

const route = useRoute();
const authStore = useAuthStore();

const loading = ref(true);
const error = ref<string | null>(null);
const movieData = ref<MovieDetailResponse | null>(null);
const addingToList = ref(false);

const isLoggedIn = computed(() => authStore.user.isLoggedIn);
const userRecord = computed(() => movieData.value?.userRecord || null);

const tmdbId = computed(() => {
  const id = route.params.tmdbId;
  return typeof id === "string" ? parseInt(id, 10) : null;
});

async function fetchMovieDetails(): Promise<void> {
  if (!tmdbId.value) {
    error.value = "Invalid movie ID";
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    const response = await axios.get<MovieDetailResponse>(getUrl(`movie/${tmdbId.value}/`));

    movieData.value = response.data;
  } catch (err) {
    console.error("Error fetching movie details:", err);
    if (isAxiosError(err) && err.response?.status === 404) {
      error.value = "Movie not found";
    } else {
      error.value = "Failed to load movie details. Please try again.";
    }
  } finally {
    loading.value = false;
  }
}

async function addToList(listId: number): Promise<void> {
  if (!tmdbId.value || !isLoggedIn.value) {
    return;
  }

  try {
    addingToList.value = true;

    await axios.post(getUrl("add-to-list-from-db/"), {
      movieId: tmdbId.value,
      listId,
    });

    // Refresh movie data to get updated user record
    void fetchMovieDetails();
  } catch (err) {
    console.error("Error adding to list:", err);

    // Check if it's an unreleased movie error
    if (
      isAxiosError(err) &&
      err.response?.data &&
      typeof err.response.data === "object" &&
      "status" in err.response.data &&
      (err.response.data as { status: unknown }).status === "unreleased"
    ) {
      error.value = "Cannot add unreleased movie to watched list. You can add it to your 'To Watch' list instead.";
    } else {
      error.value = "Failed to add movie to list. Please try again.";
    }
  } finally {
    addingToList.value = false;
  }
}

onMounted(() => {
  void fetchMovieDetails();
});
</script>

<style scoped>
.movie-detail-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
}

.loading-text {
  margin-top: 16px;
  font-size: 1.2rem;
  color: #666;
}

.error-alert {
  margin-bottom: 16px;
}

.movie-detail {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.movie-header {
  display: flex;
  gap: 32px;
  padding: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.poster-section {
  flex-shrink: 0;
}

.poster-container {
  width: 300px;
  position: relative;
}

.movie-poster {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.no-poster {
  width: 300px;
  height: 450px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.movie-info {
  flex: 1;
  min-width: 0;
}

.title-section {
  margin-bottom: 24px;
}

.movie-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 8px 0;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.original-title {
  font-size: 1.4rem;
  font-weight: 400;
  margin: 0;
  opacity: 0.9;
  font-style: italic;
}

.add-to-list-section {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.add-btn {
  font-weight: 600;
}

.disabled-watched-btn {
  opacity: 0.7;
  cursor: not-allowed;
}

.user-record-section {
  margin-bottom: 24px;
}

.record-chip {
  margin-bottom: 16px;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rating-text {
  font-weight: 500;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.metadata-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.label {
  font-weight: 600;
  min-width: 100px;
  opacity: 0.9;
}

.value {
  flex: 1;
}

.overview-section,
.links-section,
.trailers-section,
.providers-section {
  padding: 32px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.overview-section h3,
.links-section h3,
.trailers-section h3,
.providers-section h3 {
  margin: 0 0 16px 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
}

.overview-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #555;
  margin: 0;
}

.links-grid,
.trailers-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.external-link,
.trailer-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  text-decoration: none !important;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.external-link:hover,
.trailer-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.imdb-logo,
.tmdb-logo {
  width: 24px;
  height: 24px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.imdb-logo {
  background-image: url("/img/imdb.png");
}

.tmdb-logo {
  background-image: url("/img/tmdb.svg");
}

.providers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.provider-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  text-decoration: none !important;
  color: #333 !important;
  transition: all 0.3s ease;
}

.provider-link:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

.provider-logo {
  width: 40px;
  height: 40px;
  border-radius: 6px;
}

.provider-name {
  flex: 1;
  font-weight: 500;
}

@media (max-width: 768px) {
  .container {
    padding: 16px;
  }

  .movie-header {
    flex-direction: column;
    padding: 24px;
    text-align: center;
  }

  .poster-container {
    width: 250px;
    margin: 0 auto;
  }

  .movie-title {
    font-size: 2rem;
  }

  .metadata-grid {
    grid-template-columns: 1fr;
  }

  .links-grid,
  .trailers-grid {
    flex-direction: column;
  }

  .providers-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .poster-container {
    width: 200px;
  }

  .movie-title {
    font-size: 1.6rem;
  }

  .overview-section,
  .links-section,
  .trailers-section,
  .providers-section {
    padding: 20px;
  }
}
</style>
