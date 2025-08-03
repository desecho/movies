<template>
  <v-container class="trending-container">
    <div class="trending-header">
      <div class="header-content">
        <h1 class="page-title">
          <v-icon icon="mdi-trending-up" class="title-icon"></v-icon>
          Trending Movies
        </h1>
        <p class="page-subtitle">Discover what's popular right now</p>
      </div>
      <div class="trending-badge">
        <v-chip color="primary" size="large" variant="elevated">
          <v-icon start icon="mdi-fire"></v-icon>
          Hot Now
        </v-chip>
      </div>
    </div>

    <v-row v-if="movies.length > 0">
      <v-col cols="12">
        <div class="movies-section">
          <div class="section-header">
            <h2 class="section-title">Currently Trending</h2>
            <v-chip color="success" variant="outlined">{{ movies.length }} movies</v-chip>
          </div>
          <MoviesList :movies="movies" />
        </div>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col cols="12" class="text-center">
        <div class="loading-state">
          <v-progress-circular indeterminate color="primary" size="48"></v-progress-circular>
          <p class="loading-text">Loading trending movies...</p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { onMounted, ref } from "vue";

import type { MoviePreview } from "../types";
import type { AxiosError } from "axios";
import type { Ref } from "vue";

import MoviesList from "../components/MoviesList.vue";
import { getUrl } from "../helpers";
import { $toast } from "../toast";

const movies: Ref<MoviePreview[]> = ref([]);

function loadMovies(): void {
  axios
    .get(getUrl("trending/"))
    .then((response) => {
      movies.value = response.data as MoviePreview[];
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Error loading movies");
    });
}

onMounted(() => {
  loadMovies();
});
</script>

<style scoped>
.trending-container {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 2rem;
}

.trending-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  position: relative;
  overflow: hidden;
}

.trending-header::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.header-content {
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.title-icon {
  font-size: 2.5rem;
  opacity: 0.9;
}

.page-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0;
  font-weight: 400;
}

.trending-badge {
  position: relative;
  z-index: 1;
}

.movies-section {
  margin-top: 1rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.loading-state {
  padding: 4rem 2rem;
}

.loading-text {
  margin-top: 1rem;
  font-size: 1.1rem;
  color: #6c757d;
  font-weight: 500;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .trending-container {
    padding-top: 1rem;
  }

  .trending-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .page-title {
    font-size: 2rem;
    flex-direction: column;
    gap: 0.5rem;
  }

  .title-icon {
    font-size: 2rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 1.5rem;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .loading-state {
    padding: 3rem 1rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }

  .trending-header {
    padding: 1rem;
  }

  .loading-text {
    font-size: 1rem;
  }
}

/* Animation for trending badge */
.trending-badge :deep(.v-chip) {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}
</style>
