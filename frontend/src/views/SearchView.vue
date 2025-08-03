<template>
  <v-container class="search-container">
    <div class="search-header">
      <h1 class="page-title">Discover Movies</h1>
      <p class="page-subtitle">Search for movies, actors, and directors</p>
    </div>

    <v-card class="search-card" elevation="2">
      <v-card-text class="pa-6">
        <v-row align="center">
          <v-col cols="12" md="6">
            <v-form ref="form" v-model="isFormValid" lazy-validation @submit.prevent="search">
              <v-text-field
                v-model="query"
                label="Search movies, actors, directors..."
                variant="outlined"
                :hide-details="true"
                :rules="[rules.required]"
                :autofocus="true"
                prepend-inner-icon="mdi-magnify"
                class="search-input"
              ></v-text-field>
            </v-form>
          </v-col>
          <v-col cols="12" md="3">
            <v-btn color="primary" :disabled="!isFormValid" @click="search" size="large" class="search-btn" block>
              <v-icon left>mdi-magnify</v-icon>
              Search
            </v-btn>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="type"
              :items="['Movie', 'Actor', 'Director']"
              variant="outlined"
              label="Type"
              density="comfortable"
              @update:model-value="onTypeChange"
            >
            </v-select>
          </v-col>
        </v-row>

        <v-row class="mt-2">
          <v-col cols="12">
            <div class="filter-options">
              <v-checkbox
                v-model="popularOnly"
                density="comfortable"
                hide-details
                label="Show only popular"
                class="filter-checkbox"
              ></v-checkbox>
              <v-checkbox
                v-model="sortByDate"
                density="comfortable"
                hide-details
                label="Sort by date"
                class="filter-checkbox"
              ></v-checkbox>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-row v-if="movies.length > 0">
      <v-col cols="12">
        <div class="results-header">
          <h2 class="results-title">Search Results</h2>
          <v-chip color="primary" variant="outlined">{{ movies.length }} found</v-chip>
        </div>
        <MoviesList :movies="movies" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { ref } from "vue";

import type { MoviePreview } from "../types";
import type { AxiosError } from "axios";
import type { Ref } from "vue";

import MoviesList from "../components/MoviesList.vue";
import { useFormValidation } from "../composables/formValidation";
import { getUrl, rulesHelper } from "../helpers";
import { $toast } from "../toast";

const rules = rulesHelper;

const isFormValid = ref(false);
const movies: Ref<MoviePreview[]> = ref([]);
const query = ref("");
const type = ref("Movie");
const typeCode = ref("movie");
const popularOnly = ref(true);
const sortByDate = ref(false);

const { form, isValid } = useFormValidation();

function onTypeChange(type_: string): void {
  switch (type_) {
    case "Movie":
      typeCode.value = "movie";
      break;
    case "Actor":
      typeCode.value = "actor";
      break;
    case "Director":
      typeCode.value = "director";
      break;
    default:
      typeCode.value = "movie";
  }
}

async function search(): Promise<void> {
  if (!(await isValid())) {
    return;
  }
  const options = {
    popularOnly: popularOnly.value,
    sortByDate: sortByDate.value,
  };
  const data = {
    query: query.value,
    type: typeCode.value,
    options: JSON.stringify(options),
  };

  axios
    .get(getUrl("search/"), { params: data })
    .then((response) => {
      const ms: MoviePreview[] = response.data as MoviePreview[];
      if (ms.length === 0) {
        $toast.info("Nothing has been found");
      }
      ms.forEach((m: MoviePreview) => {
        m.hidden = false;
      });

      movies.value = ms;
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Search error");
    });
}
</script>

<style scoped>
.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 2rem;
}

.search-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  font-weight: 400;
  margin: 0;
}

.search-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
}

.search-input {
  :deep(.v-field) {
    border-radius: 12px;
  }

  :deep(.v-field__input) {
    font-size: 1.1rem;
  }
}

.search-btn {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  font-size: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
}

.filter-options {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.filter-checkbox {
  :deep(.v-label) {
    font-weight: 500;
    color: #495057;
  }

  :deep(.v-selection-control__input) {
    .v-icon {
      color: #667eea;
    }
  }
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.results-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .search-container {
    padding-top: 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }

  .search-card :deep(.v-card-text) {
    padding: 1.5rem !important;
  }

  .filter-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .results-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .results-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }

  .search-card :deep(.v-card-text) {
    padding: 1rem !important;
  }
}
</style>
