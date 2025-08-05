<template>
  <v-container class="recommendations-container">
    <div class="recommendations-header">
      <div class="header-content">
        <h1 class="page-title">
          <v-icon icon="mdi-robot" class="title-icon"></v-icon>
          AI Movie Recommendations
        </h1>
        <p class="page-subtitle">Get personalized movie suggestions powered by AI</p>
      </div>
      <div class="ai-badge">
        <v-chip color="secondary" size="large" variant="elevated">
          <v-icon start icon="mdi-brain"></v-icon>
          AI Powered
        </v-chip>
      </div>
    </div>

    <!-- Preferences Form -->
    <v-card class="preferences-card mb-6" elevation="2">
      <v-card-title class="preferences-title">
        <v-icon icon="mdi-tune" class="me-2"></v-icon>
        Customize Your Preferences
      </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="getRecommendations">
          <v-row>
            <!-- Preferred Genre -->
            <v-col cols="12" md="6">
              <v-select
                v-model="preferences.preferredGenre"
                :items="MOVIE_GENRES"
                label="Preferred Genre"
                prepend-inner-icon="mdi-movie"
                clearable
                variant="outlined"
                density="comfortable"
              ></v-select>
            </v-col>

            <!-- Number of Recommendations -->
            <v-col cols="12" md="6">
              <div class="slider-section">
                <label class="slider-label" title="Choose a number that is more than your actual desired recommendations. You won't get exactly that many">Desired Number of Recommendations</label>
                <v-slider
                  v-model="preferences.recommendationsNumber"
                  :min="AI_MIN_RECOMMENDATIONS"
                  :max="AI_MAX_RECOMMENDATIONS"
                  :step="1"
                  thumb-label
                  show-ticks="always"
                  tick-size="4"
                  color="primary"
                  class="mt-2"
                  title="Choose a number that is more than your actual desired recommendations. You won't get exactly that many"
                ></v-slider>
              </div>
            </v-col>

            <!-- Minimum Rating -->
            <v-col cols="12" md="6">
              <div class="rating-section">
                <label class="slider-label">Minimum Rating</label>
                <v-rating
                  v-model="preferences.minRating"
                  :length="AI_MAX_RATING"
                  color="amber"
                  size="large"
                  class="mt-2"
                  clearable
                ></v-rating>
                <div class="rating-text">{{ preferences.minRating ? preferences.minRating : "Any" }} stars</div>
              </div>
            </v-col>

            <!-- Year Range -->
            <v-col cols="12" md="6">
              <div class="year-range-section">
                <label class="slider-label">Year Range</label>
                <v-range-slider
                  v-model="yearRange"
                  :min="1920"
                  :max="currentYear"
                  :step="1"
                  thumb-label
                  color="primary"
                  class="mt-2"
                ></v-range-slider>
                <div class="year-range-text">{{ yearRange[0] }} - {{ yearRange[1] }}</div>
              </div>
            </v-col>
          </v-row>

          <v-row class="mt-4">
            <v-col class="text-center">
              <v-btn
                type="submit"
                color="primary"
                size="large"
                variant="elevated"
                :loading="loading"
                prepend-icon="mdi-magic-staff"
              >
                Get AI Recommendations
              </v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Recommendations Results -->
    <div v-if="movies.length > 0" class="recommendations-results">
      <div class="section-header">
        <h2 class="section-title">Your AI Recommendations</h2>
        <v-chip color="success" variant="outlined">{{ movies.length }} movies</v-chip>
      </div>
      <MoviesList :movies="movies" />
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="loading-state">
      <v-progress-circular indeterminate color="primary" size="48"></v-progress-circular>
      <p class="loading-text">AI is analyzing your preferences...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="hasSearched && movies.length === 0" class="empty-state">
      <v-icon icon="mdi-robot-confused" size="64" color="grey"></v-icon>
      <h3>No recommendations found</h3>
      <p>Try adjusting your preferences and search again.</p>
    </div>

    <!-- Getting Started -->
    <div v-else class="getting-started">
      <v-card class="text-center pa-8" variant="outlined">
        <v-icon icon="mdi-lightbulb" size="64" color="primary" class="mb-4"></v-icon>
        <h3 class="mb-4">Ready to discover new movies?</h3>
        <p class="mb-4">Set your preferences above and let our AI recommend movies tailored just for you!</p>
        <v-btn color="primary" variant="text" @click="scrollToTop">
          <v-icon start icon="mdi-arrow-up"></v-icon>
          Set Preferences
        </v-btn>
      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { computed, onMounted, ref } from "vue";

import type { MoviePreview } from "../types";
import type { AxiosError } from "axios";
import type { Ref } from "vue";

import MoviesList from "../components/MoviesList.vue";
import { AI_MAX_RATING, AI_MAX_RECOMMENDATIONS, AI_MIN_RATING, AI_MIN_RECOMMENDATIONS, MOVIE_GENRES } from "../const";
import { getUrl } from "../helpers";
import { $toast } from "../toast";

interface RecommendationPreferences {
  preferredGenre: string | null;
  recommendationsNumber: number;
  minRating: number | null;
}

const movies: Ref<MoviePreview[]> = ref([]);
const loading = ref(false);
const hasSearched = ref(false);

const preferences: Ref<RecommendationPreferences> = ref({
  preferredGenre: null,
  recommendationsNumber: AI_MAX_RECOMMENDATIONS,
  minRating: null,
});

const yearRange = ref([2000, new Date().getFullYear()]);

const currentYear = computed(() => new Date().getFullYear());

function scrollToTop(): void {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function getRecommendations(): Promise<void> {
  loading.value = true;
  hasSearched.value = true;

  try {
    const params = new URLSearchParams();

    if (preferences.value.preferredGenre) {
      params.append("preferredGenre", preferences.value.preferredGenre);
    }

    if (preferences.value.minRating && preferences.value.minRating >= AI_MIN_RATING) {
      params.append("minRating", preferences.value.minRating.toString());
    }

    params.append("recommendationsNumber", preferences.value.recommendationsNumber.toString());
    params.append("yearStart", yearRange.value[0].toString());
    params.append("yearEnd", yearRange.value[1].toString());

    const response = await axios.get(getUrl(`recommendations/?${params.toString()}`));
    movies.value = response.data as MoviePreview[];

    if (movies.value.length === 0) {
      $toast.info("No recommendations found for your preferences. Try adjusting them!");
    } else {
      $toast.success(`Found ${movies.value.length} AI recommendations for you!`);
    }
  } catch (error: unknown) {
    const axiosError = error as AxiosError;
    console.error("Error getting AI recommendations:", axiosError);

    // Handle authentication errors
    if (axiosError.response?.status === 401) {
      $toast.error("Please log in to get AI recommendations.");
      // The axios interceptor should handle redirecting to login
      movies.value = [];
      return;
    }

    if (
      axiosError.response?.data &&
      typeof axiosError.response.data === "object" &&
      "error" in axiosError.response.data
    ) {
      $toast.error(`Error: ${(axiosError.response.data as { error: string }).error}`);
    } else {
      $toast.error("Failed to get AI recommendations. Please try again.");
    }
    movies.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  // Set default preferences on mount
  preferences.value.recommendationsNumber = AI_MAX_RECOMMENDATIONS;
});
</script>

<style scoped>
.recommendations-container {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 2rem;
}

.recommendations-header {
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

.recommendations-header::before {
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

.ai-badge {
  position: relative;
  z-index: 1;
}

.preferences-card {
  background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%);
  border: 1px solid #e9ecef;
}

.preferences-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  padding-bottom: 1rem;
}

.slider-section,
.rating-section,
.year-range-section {
  margin-bottom: 1rem;
}

.slider-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
  display: block;
  margin-bottom: 0.5rem;
}

.rating-text,
.year-range-text {
  font-size: 0.875rem;
  color: #6c757d;
  text-align: center;
  margin-top: 0.5rem;
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

.loading-state,
.empty-state,
.getting-started {
  padding: 4rem 2rem;
  text-align: center;
}

.loading-text {
  margin-top: 1rem;
  font-size: 1.1rem;
  color: #6c757d;
  font-weight: 500;
}

.empty-state h3 {
  margin: 1rem 0 0.5rem 0;
  color: #4a5568;
}

.empty-state p {
  color: #6c757d;
  margin: 0;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .recommendations-container {
    padding-top: 1rem;
  }

  .recommendations-header {
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

  .loading-state,
  .empty-state,
  .getting-started {
    padding: 3rem 1rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }

  .recommendations-header {
    padding: 1rem;
  }

  .loading-text {
    font-size: 1rem;
  }
}

/* Animation for AI badge */
.ai-badge :deep(.v-chip) {
  animation: glow 3s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    box-shadow: 0 0 5px rgba(124, 75, 162, 0.3);
  }
  to {
    box-shadow: 0 0 20px rgba(124, 75, 162, 0.6);
  }
}
</style>
