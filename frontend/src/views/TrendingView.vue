<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <MoviesList :movies="movies" />
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
