<template>
  <div class="results">
    <div v-for="movie in movies" v-show="!movie.hidden" :key="movie.id" class="movie">
      <div class="poster-wrapper">
        <div class="poster">
          <div v-if="isLoggedIn" class="add-to-list-buttons">
            <a
              v-show="movie.isReleased"
              href="javascript:void(0)"
              title='Add to the list "Watched"'
              @click="addToListFromDb(movie, listWatchedId)"
            >
              <v-icon icon="mdi-eye" />
            </a>
            <a
              href="javascript:void(0)"
              title='Add to the list "To Watch"'
              @click="addToListFromDb(movie, listToWatchId)"
              ><v-icon icon="mdi-eye-off"
            /></a>
          </div>
          <a :href="movie.tmdbLink" target="_blank">
            <v-lazy-image
              :srcset="getSrcSet(movie.poster, movie.poster2x)"
              :src="movie.poster2x"
              :title="movie.titleOriginal"
              :alt="movie.title"
            />
          </a>
        </div>
      </div>
      <div class="movie-content">
        <div class="title">{{ movie.title }}</div>
        <div v-show="movie.releaseDate" class="details">
          {{ movie.releaseDate }}
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import axios from "axios";
import VLazyImage from "v-lazy-image";

import type { AddToListFromDbResponseData, MoviePreview } from "../types";
import type { AxiosError } from "axios";

import { listToWatchId, listWatchedId } from "../const";
import { getSrcSet, getUrl } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { useRecordsStore } from "../stores/records";
import { $toast } from "../toast";

defineProps<{
  movies: MoviePreview[];
}>();

const { user } = useAuthStore();
const isLoggedIn = user.isLoggedIn;

async function addToListFromDb(movie: MoviePreview, listId: number): Promise<void> {
  await axios
    .post(getUrl("add-to-list-from-db/"), {
      movieId: movie.id,
      listId,
    })
    .then((response) => {
      const data = response.data as AddToListFromDbResponseData;
      if (data.status === "not_found") {
        $toast.error("Movie is not found in the database");
        return;
      }
      movie.hidden = true;
    })
    .catch(() => {
      $toast.error("Error adding a movie");
    });
  const { reloadRecords } = useRecordsStore();
  reloadRecords()
    .then(() => {
      console.log("Records reloaded");
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Error reloading records");
    });
}
</script>

<style scoped>
.results {
  clear: both;
  margin-top: 20px;
  padding: 0;
}

.title {
  font-size: 1em;
  font-weight: bold;
  line-height: 20px;
  display: inline;
}

.add-to-list-buttons {
  display: inline;
  position: absolute;
  right: 18px;
  bottom: 14px;
  background-color: white;
  opacity: 0.7;
  border-radius: 5px;

  a {
    margin: 0 10px;
  }
}

.poster {
  position: relative;

  img {
    width: 150px;
    height: auto;
    border-radius: 5px;
  }
}

.movie {
  min-height: 160px;
  margin-bottom: 10px;
  margin-right: 10px;
  padding: 10px;
  display: inline-grid;
  width: 150px;
}

.movie-content {
  margin-left: 10px;
  width: 150px;
}

.poster-wrapper {
  height: 227px;
}
</style>
