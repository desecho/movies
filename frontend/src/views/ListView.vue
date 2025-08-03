<template>
  <v-container>
    <!-- Profile header (only show when viewing another user's profile) -->
    <v-row v-if="isProfileView">
      <v-col cols="12">
        <div class="profile-header">
          <h2>{{ username }}'s Movies</h2>
          <!-- List selector for profile views -->
          <div class="profile-list-selector">
            <v-btn-toggle v-model="selectedProfileList" density="compact" mandatory>
              <v-btn :value="listWatchedId" :size="modeButtonSize"> Watched </v-btn>
              <v-btn :value="listToWatchId" :size="modeButtonSize"> To Watch </v-btn>
            </v-btn-toggle>
          </div>
        </div>
      </v-col>
    </v-row>

    <div class="controls-section">
      <v-row>
        <v-col cols="12" md="6">
          <div class="control-group">
            <label class="control-label">View Mode</label>
            <v-btn-toggle v-model="mode" density="compact" mandatory>
              <v-btn value="full" :size="modeButtonSize">Full</v-btn>
              <v-btn value="compact" :size="modeButtonSize">Compact</v-btn>
              <v-btn value="minimal" :size="modeButtonSize">Minimal</v-btn>
              <v-btn value="gallery" :size="modeButtonSize">Gallery</v-btn>
            </v-btn-toggle>
          </div>
        </v-col>
        <v-col cols="12" md="6">
          <div class="control-group">
            <label class="control-label">Sort By</label>
            <v-btn-toggle v-model="sort" density="compact" mandatory>
              <v-btn value="releaseDate" :size="sortButtonSize">Release date</v-btn>
              <v-btn value="rating" :size="sortButtonSize">Rating</v-btn>
              <v-btn value="additionDate" :size="sortButtonSize">Date added</v-btn>
              <v-btn v-if="currentListId == listToWatchId && !isProfileView" value="custom" :size="sortButtonSize">
                Custom
              </v-btn>
            </v-btn-toggle>
          </div>
        </v-col>
      </v-row>
    </div>
    <v-row>
      <v-col cols="6">
        <v-text-field
          v-model="query"
          label="Search"
          variant="solo"
          :hide-details="true"
          class="mr-5"
          density="compact"
        ></v-text-field>
      </v-col>
      <v-col cols="1"></v-col>
      <v-col v-if="areRecordsLoaded" cols="5">
        <v-icon icon="mdi-eye" /> {{ watchedCount }} <v-icon icon="mdi-eye-off" /> {{ toWatchCount }}
      </v-col>
    </v-row>
    <v-row v-if="areRecordsLoaded">
      <v-col cols="10">
        <v-pagination v-model="page" :pages="totalPages" :range-size="1" active-color="#DCEDFF" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <div v-cloak v-if="mode != 'gallery'">
          <draggable v-model="records" item-key="id" :disabled="!isSortable" @sort="saveRecordsOrder">
            <template #item="{ element, index }">
              <div
                v-if="paginatedRecords.includes(element)"
                class="movie"
                :class="{
                  'movie-minimal': mode == 'minimal',
                  'movie-full': mode == 'full',
                  draggable: isSortable,
                }"
              >
                <!-- Movie title banner spanning full width at the very top -->
                <div class="movie-title-banner">
                  <h2 class="movie-title" :title="element.movie.titleOriginal">
                    {{ element.movie.title }}
                  </h2>
                </div>

                <!-- Movie card content below title -->
                <div class="movie-card-content">
                  <div v-show="mode != 'minimal'" class="poster">
                    <!-- Action buttons overlay on poster -->
                    <div class="poster-overlay-buttons">
                      <!-- Only show action buttons for own lists -->
                      <div v-if="!isProfileView" class="remove-button">
                        <a href="javascript:void(0)" title="Delete" @click="removeRecord(element, index)">
                          <v-icon icon="mdi-trash-can" />
                        </a>
                      </div>
                      <!-- Add to list buttons - show for logged in users viewing profile -->
                      <div v-if="isProfileView && authStore.user.isLoggedIn" class="add-to-my-list-buttons">
                        <v-btn
                          v-if="!isMovieInMyList(element.movie.id)"
                          size="x-small"
                          color="primary"
                          variant="outlined"
                          title="Add to my Watched list"
                          @click="addToMyList(element.movie.id, listWatchedId)"
                        >
                          <v-icon icon="mdi-eye" />
                        </v-btn>
                        <v-btn
                          v-if="!isMovieInMyList(element.movie.id)"
                          size="x-small"
                          color="secondary"
                          variant="outlined"
                          title="Add to my To Watch list"
                          @click="addToMyList(element.movie.id, listToWatchId)"
                        >
                          <v-icon icon="mdi-eye-off" />
                        </v-btn>
                        <span v-if="isMovieInMyList(element.movie.id)" class="already-in-list">
                          <v-icon icon="mdi-check" color="success" />
                          In your list
                        </span>
                      </div>
                      <div v-if="!isProfileView" class="add-to-list-buttons">
                        <div v-if="currentListId == listToWatchId">
                          <a
                            v-show="element.movie.isReleased && element.listId != listWatchedId"
                            href="javascript:void(0)"
                            title='Add to "Watched" list'
                            @click="addToList(element.movie.id, listWatchedId, element)"
                          >
                            <v-icon icon="mdi-eye" />
                          </a>
                        </div>
                        <div v-if="currentListId == listWatchedId">
                          <a
                            v-show="element.listId != listToWatchId"
                            href="javascript:void(0)"
                            title='Add to "To Watch" list'
                            @click="addToList(element.movie.id, listToWatchId, element)"
                          >
                            <v-icon icon="mdi-eye-off" />
                          </a>
                        </div>
                      </div>
                    </div>
                    <span v-if="mode == 'full'">
                      <v-lazy-image
                        class="poster-big"
                        :srcset="getSrcSet(element.movie.posterNormal, element.movie.posterBig)"
                        :src="element.movie.posterBig"
                        :title="element.movie.titleOriginal"
                        :alt="element.movie.title"
                      />
                    </span>
                    <span v-else>
                      <v-lazy-image
                        class="poster-small"
                        :srcset="getSrcSet(element.movie.posterSmall, element.movie.posterNormal)"
                        :src="element.movie.posterNormal"
                        :title="element.movie.titleOriginal"
                        :alt="element.movie.title"
                      />
                    </span>
                  </div>
                  <div
                    class="details"
                    :class="{
                      'details-minimal': mode == 'minimal',
                    }"
                  >
                    <div v-show="element.movie.imdbRating" class="imdb-rating">
                      <span class="item-desc">IMDb Rating:</span>
                      {{ element.movie.imdbRating }}
                    </div>
                    <div v-show="element.movie.isReleased" class="release-date">
                      <span v-show="mode != 'minimal'" class="item-desc">Release Date:</span>
                      {{ element.movie.releaseDate }}
                    </div>
                    <div v-show="mode == 'full'">
                      <div v-show="element.movie.country">
                        <span class="item-desc">Country:</span>
                        {{ element.movie.country }}
                      </div>
                      <div v-show="element.movie.director">
                        <span class="item-desc">Director:</span>
                        {{ element.movie.director }}
                      </div>
                      <div v-show="element.movie.writer">
                        <span class="item-desc">Writer:</span>
                        {{ element.movie.writer }}
                      </div>
                      <div v-show="element.movie.genre">
                        <span class="item-desc">Genre:</span>
                        {{ element.movie.genre }}
                      </div>
                      <div v-show="element.movie.actors">
                        <span class="item-desc">Actors:</span>
                        {{ element.movie.actors }}
                      </div>
                      <div v-show="element.movie.runtime">
                        <span class="item-desc">Runtime:</span>
                        {{ element.movie.runtime }}
                      </div>
                      <div v-show="element.movie.overview">
                        <span class="item-desc">Overview:</span>
                        {{ element.movie.overview }}
                      </div>
                      <div class="urls">
                        <div v-show="element.movie.homepage" class="website-link-container">
                          <a :href="element.movie.homepage" target="_blank" class="website-link">
                            <v-icon icon="mdi-web" size="small" class="website-icon" />
                            Website
                            <v-icon icon="mdi-open-in-new" size="x-small" class="external-icon" />
                          </a>
                        </div>
                        <a :href="element.movie.imdbUrl" target="_blank"><span class="imdb"></span></a>
                        <a :href="element.movie.tmdbUrl" target="_blank"><span class="tmdb"></span></a>
                      </div>
                      <div v-show="element.movie.trailers.length">
                        <span class="item-desc">Trailers:</span>
                        <div class="trailers">
                          <a
                            v-for="trailer in element.movie.trailers"
                            :key="trailer.name"
                            :href="trailer.url"
                            target="_blank"
                            >{{ trailer.name }}</a
                          >
                        </div>
                      </div>
                      <div v-show="element.providerRecords.length">
                        <span class="item-desc">Stream on:</span>
                        <div>
                          <a
                            v-for="providerRecord in element.providerRecords"
                            :key="providerRecord.provider"
                            :href="providerRecord.tmdbWatchUrl"
                            target="_blank"
                          >
                            <v-lazy-image
                              class="provider"
                              :src="providerRecord.provider.logo"
                              :title="providerRecord.provider.name"
                              :alt="providerRecord.provider.name"
                            />
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div
                    class="review"
                    :class="{
                      'review-minimal': mode == 'minimal',
                    }"
                  >
                    <div v-if="currentListId == listWatchedId">
                      <!-- Show ratings for profile views, but make them read-only -->
                      <star-rating
                        v-model:rating="element.rating"
                        :star-size="starSize"
                        :show-rating="false"
                        :clearable="!isProfileView"
                        :read-only="isProfileView"
                        @update:rating="changeRating(element, $event)"
                      >
                      </star-rating>
                      <!-- Only show comment editing for own lists -->
                      <div
                        v-if="!isProfileView"
                        v-show="(element.comment || element.commentArea) && mode != 'minimal'"
                        class="comment"
                      >
                        <div>
                          <v-textarea v-model="element.comment" class="form-control" title="Comment"> </v-textarea>
                        </div>
                        <button type="button" class="btn btn-secondary" title="Save" @click="saveComment(element)">
                          <v-icon icon="mdi-content-save" />
                        </button>
                      </div>
                      <!-- Show comments read-only for profile views -->
                      <div v-if="isProfileView && element.comment && mode != 'minimal'" class="comment-readonly">
                        <p>{{ element.comment }}</p>
                      </div>
                      <button
                        v-if="!isProfileView"
                        v-show="element.comment == '' && !element.commentArea && mode != 'minimal'"
                        type="button"
                        class="btn btn-secondary"
                        title="Add comment"
                        @click="showCommentArea(element)"
                      >
                        <v-icon icon="mdi-comment" />
                      </button>
                      <!-- Only show options for own lists -->
                      <div v-if="!isProfileView" v-show="mode == 'full'" class="option-buttons">
                        <div>
                          <label :for="'original_' + element.id">Watched original version</label>
                          <input
                            :id="'original_' + element.id"
                            v-model="element.options.original"
                            type="checkbox"
                            @change="saveOptions(element, 'original')"
                          />
                        </div>
                        <div>
                          <label :for="'extended_' + element.id">Watched extended version</label>
                          <input
                            :id="'extended_' + element.id"
                            v-model="element.options.extended"
                            type="checkbox"
                            @change="saveOptions(element, 'extended')"
                          />
                        </div>
                        <div>
                          <label :for="'theatre_' + element.id">Watched in theatre</label>
                          <input
                            :id="'theatre_' + element.id"
                            v-model="element.options.theatre"
                            type="checkbox"
                            @change="saveOptions(element, 'theatre')"
                          />
                        </div>
                        <div>
                          <label :for="'hd_' + element.id">Watched in HD</label>
                          <input
                            :id="'hd_' + element.id"
                            v-model="element.options.hd"
                            type="checkbox"
                            @change="saveOptions(element, 'hd')"
                          />
                        </div>
                        <div>
                          <label :for="'full_hd_' + element.id">Watched in FullHD</label>
                          <input
                            :id="'full_hd_' + element.id"
                            v-model="element.options.fullHd"
                            type="checkbox"
                            @change="saveOptions(element, 'fullHd')"
                          />
                        </div>
                        <div>
                          <label :for="'4k_' + element.id">Watched in 4K</label>
                          <input
                            :id="'4k_' + element.id"
                            v-model="element.options.ultraHd"
                            type="checkbox"
                            @change="saveOptions(element, 'ultraHd')"
                          />
                        </div>
                      </div>
                      <div></div>
                    </div>
                    <div class="clearfix"></div>
                  </div>
                </div>
                <!-- Close movie-card-content -->
              </div>
            </template>
          </draggable>
        </div>
        <div v-cloak v-if="mode === 'gallery'" id="gallery">
          <draggable v-model="records" item-key="id" :disabled="!isSortable" @sort="saveRecordsOrder">
            <template #item="{ element, index }">
              <div v-if="paginatedRecords.includes(element)" class="gallery-record">
                <!-- Only show move buttons for own lists -->
                <div v-if="!isProfileView" class="buttons">
                  <button
                    v-show="isSortable"
                    type="button"
                    class="up-button"
                    title="Move to the top"
                    @click="moveToTop(element, index)"
                  >
                    <v-icon icon="mdi-arrow-up" />
                  </button>
                  <button
                    v-show="isSortable"
                    type="button"
                    class="down-button"
                    title="Move to the bottom"
                    @click="moveToBottom(element, index)"
                  >
                    <v-icon icon="mdi-arrow-down" />
                  </button>
                </div>
                <v-lazy-image
                  class="poster-big"
                  :class="{ draggable: isSortable }"
                  :srcset="getSrcSet(element.movie.posterNormal, element.movie.posterBig)"
                  :src="element.movie.posterBig"
                  :title="element.movie.title"
                  :alt="element.movie.title"
                />
              </div>
            </template>
          </draggable>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="areRecordsLoaded">
      <v-col cols="10">
        <v-pagination v-model="page" :pages="totalPages" :range-size="1" active-color="#DCEDFF" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import VPagination from "@hennge/vue3-pagination";
import axios from "axios";
import { cloneDeep } from "lodash";
import VLazyImage from "v-lazy-image";
import { computed, onMounted, ref, toRef, watch } from "vue";
import StarRating from "vue-star-rating";
import Draggable from "vuedraggable";

import type { RecordType, SortData } from "../types";

import { useMobile } from "../composables/mobile";
import { listToWatchId, listWatchedId, starSizeMinimal, starSizeNormal } from "../const";
import { getSrcSet, getUrl } from "../helpers";
import { useAuthStore } from "../stores/auth"; // Import auth store
import { useRecordsStore } from "../stores/records";
import { $toast } from "../toast";

const props = defineProps<{
  listId: number;
  username?: string;
  isProfileView?: boolean;
}>();

const { isMobile } = useMobile();

const recordsStore = useRecordsStore();
const authStore = useAuthStore(); // Initialize auth store

const mode = ref("full");
const sort = ref("additionDate");
const query = ref("");
const records = toRef(recordsStore, "records");
const areRecordsLoaded = toRef(recordsStore, "areLoaded");

// For profile views, allow switching between lists
const selectedProfileList = ref(props.listId);

// Track loading state for add to list buttons
const addingToList = ref<Record<string, boolean>>({});

// Store user's own records for checking if movie already exists
const myRecords = ref<RecordType[]>([]);

const page = ref(1);
const perPage = 50;

// Computed property to get the current list ID (either from props or selected in profile)
const currentListId = computed(() => {
  return props.isProfileView ? selectedProfileList.value : props.listId;
});

const filteredRecords = computed(() => {
  const q = query.value.trim().toLowerCase();
  return records.value.filter((record) => {
    return (
      (record.movie.title.toLowerCase().includes(q) || record.movie.titleOriginal.toLowerCase().includes(q)) &&
      record.listId === currentListId.value
    );
  });
});

const watchedCount = computed(() => {
  return records.value.filter((record) => record.listId === listWatchedId).length;
});

const toWatchCount = computed(() => {
  return records.value.filter((record) => record.listId === listToWatchId).length;
});

const totalPages = computed(() => Math.ceil(filteredRecords.value.length / perPage));
const modeButtonSize = computed(() => {
  if (isMobile.value) {
    return "small";
  }
  return "default";
});

const sortButtonSize = computed(() => {
  if (isMobile.value) {
    return "x-small";
  }
  return "default";
});

const paginatedRecords = computed(() => {
  const start = (page.value - 1) * perPage;
  return filteredRecords.value.slice(start, start + perPage);
});

function sortRecords(): void {
  const recordsCopy = cloneDeep(records.value);

  switch (sort.value) {
    case "custom":
      recordsCopy.sort((a, b) => {
        return a.order - b.order;
      });
      break;
    case "releaseDate":
      recordsCopy.sort((a, b) => {
        return b.movie.releaseDateTimestamp - a.movie.releaseDateTimestamp;
      });
      break;
    case "rating":
      if (currentListId.value === listWatchedId) {
        recordsCopy.sort((a, b) => {
          return b.rating - a.rating;
        });
      } else {
        recordsCopy.sort((a, b) => {
          return b.movie.imdbRating - a.movie.imdbRating;
        });
      }
      break;
    default:
      recordsCopy.sort((a, b) => {
        return b.additionDate - a.additionDate;
      });
  }

  records.value = recordsCopy;
}

watch(sort, () => {
  sortRecords();
});

const listIdRef = toRef(props, "listId");
const usernameRef = toRef(props, "username");
const isProfileViewRef = toRef(props, "isProfileView");

async function loadRecordsData(): Promise<void> {
  const { loadRecords } = useRecordsStore();

  try {
    if (props.isProfileView && props.username) {
      await loadRecords(props.username);
    } else {
      await loadRecords();
    }
  } catch (error: unknown) {
    console.log(error);
    const errorMessage =
      props.isProfileView && props.username ? `Error loading ${props.username}'s movies` : "Error loading movies";
    $toast.error(errorMessage);
  }
}

// Load user's own records when viewing a profile (if logged in)
async function loadMyRecords(): Promise<void> {
  if (props.isProfileView && authStore.user.isLoggedIn) {
    try {
      const response = await axios.get(getUrl("records/"));
      myRecords.value = response.data as RecordType[];
    } catch (error) {
      console.log("Error loading user's records:", error);
    }
  }
}

// Check if a movie is already in user's list
function isMovieInMyList(movieId: number): boolean {
  if (!props.isProfileView || !authStore.user.isLoggedIn || !myRecords.value.length) {
    return false;
  }
  return myRecords.value.some((record) => record.movie.id === movieId);
}

// Add movie to user's own list
function addToMyList(movieId: number, listId: number): void {
  if (!authStore.user.isLoggedIn) {
    $toast.error("You must be logged in to add movies to your list");
    return;
  }

  const loadingKey = `${movieId}-${listId}`;
  addingToList.value[loadingKey] = true;

  try {
    // Add to myRecords for immediate UI update
    const movieData = records.value.find((record) => record.movie.id === movieId)?.movie;
    if (movieData) {
      const newRecord: RecordType = {
        id: Date.now(),
        movie: movieData,
        listId,
        rating: 0,
        comment: "",
        additionDate: Date.now(),
        order: myRecords.value.length + 1,
        options: {
          original: false,
          extended: false,
          theatre: false,
          hd: false,
          fullHd: false,
          ultraHd: false,
        },
        providerRecords: [],
        ratingOriginal: 0,
        commentArea: false,
      };
      myRecords.value.push(newRecord);
    }

    const listName = listId === listWatchedId ? "Watched" : "To Watch";
    $toast.success(`Movie added to your ${listName} list`);
  } catch (error) {
    console.log("Error adding movie to list:", error);
    $toast.error("Error adding movie to your list");
  } finally {
    addingToList.value[loadingKey] = false;
  }
}

// Watch for changes in props that require reloading data
watch([listIdRef, usernameRef, isProfileViewRef], async () => {
  selectedProfileList.value = props.listId; // Reset profile list selector
  sortRecords();
  // Force reload records when switching contexts
  await loadRecordsData();
  await loadMyRecords(); // Load user's records if viewing profile
});

// Watch for profile list selection changes
watch(selectedProfileList, () => {
  sortRecords();
  page.value = 1; // Reset to first page when switching lists
});

// Watch for login status changes
watch(
  () => authStore.user.isLoggedIn,
  async (isLoggedIn) => {
    if (isLoggedIn && props.isProfileView) {
      await loadMyRecords();
    } else if (!isLoggedIn) {
      myRecords.value = [];
    }
  },
);

const starSize = computed(() => {
  if (mode.value === "minimal") {
    return starSizeMinimal;
  }
  return starSizeNormal;
});

const isSortable = computed(() => {
  return (
    currentListId.value === listToWatchId &&
    sort.value === "custom" &&
    (mode.value === "minimal" || mode.value === "gallery") &&
    !props.isProfileView // Disable sorting for profile views
  );
});

function saveRecordsOrder(): void {
  function getSortData(): SortData[] {
    const data: SortData[] = [];
    records.value.forEach((record, index) => {
      const sortData = { id: record.id, order: index + 1 };
      data.push(sortData);
    });
    return data;
  }

  axios.put(getUrl("save-records-order/"), { records: getSortData() }).catch(() => {
    $toast.error("Error saving movie order");
  });
}

function changeRating(record: RecordType, rating: number): void {
  axios
    .put(getUrl(`change-rating/${record.id}/`), { rating })
    .then(() => {
      record.ratingOriginal = record.rating;
    })
    .catch(() => {
      record.rating = record.ratingOriginal;
      $toast.error("Error saving the rating");
    });
}

function saveOptions(record: RecordType, field: keyof RecordType["options"]): void {
  const data = {
    options: record.options,
  };

  axios.put(getUrl(`record/${record.id}/options/`), data).catch(() => {
    record.options[field] = !record.options[field];
    $toast.error("Error saving options");
  });
}

function removeRecord(record: RecordType, index: number): void {
  axios
    .delete(getUrl(`remove-record/${record.id}/`))
    .then(() => {
      records.value.splice(index, 1);
    })
    .catch(() => {
      $toast.error("Error removing the movie");
    });
}

function addToList(movieId: number, listId: number, record: RecordType): void {
  axios
    .post(getUrl(`add-to-list/${movieId}/`), {
      listId,
    })
    .then(() => {
      record.listId = listId;
      record.additionDate = Date.now();
    })
    .catch(() => {
      $toast.error("Error adding the movie to the list");
    });
}

function showCommentArea(record: RecordType): void {
  record.commentArea = true;
}

function saveComment(record: RecordType): void {
  const data = {
    comment: record.comment,
  };
  axios
    .put(getUrl(`save-comment/${record.id}/`), data)
    .then(() => {
      if (record.comment === "") {
        record.commentArea = false;
      }
    })
    .catch(() => {
      $toast.error("Error saving a comment");
    });
}

function moveToTop(record: RecordType, index: number): void {
  records.value.splice(index, 1);
  records.value.unshift(record);
  saveRecordsOrder();
}

function moveToBottom(record: RecordType, index: number): void {
  records.value.splice(index, 1);
  records.value.push(record);
  saveRecordsOrder();
}

onMounted(async () => {
  await loadRecordsData();
  await loadMyRecords(); // Load user's records if viewing profile and logged in
});
</script>

<style src="@hennge/vue3-pagination/dist/vue3-pagination.css"></style>
<style scoped>
.profile-header {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.profile-header h2 {
  margin: 0 0 15px 0;
  color: #333;
}

.profile-list-selector {
  display: flex;
  justify-content: center;
}

.comment-readonly {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #ddd;
  max-width: 400px;
}

.option-buttons-readonly {
  margin-top: 10px;
  font-size: 0.9em;
  color: #666;
}

.option-buttons-readonly div {
  margin: 5px 0;
}

.option-buttons {
  input {
    margin-left: 5px;
  }
}

.poster {
  flex-shrink: 0;
  margin-right: 0;
  margin-bottom: 0;
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;

  img {
    border-radius: 12px;
    transition: transform 0.3s ease;
    width: auto;
    height: auto;
    display: block;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);

    img {
      transform: scale(1.03);
    }
  }
}

.poster-small {
  width: 92px;
}

#query {
  text-align: right;
}

.movie {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
  padding: 24px;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  align-items: stretch;

  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
    border-color: rgba(102, 126, 234, 0.2);
  }

  .movie-content {
    flex: 1;
    min-width: 0;
  }
}

.movie-minimal {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  margin: 12px 0;
  padding: 16px 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  min-height: auto;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 16px;

  &::before {
    height: 2px;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.9);
    transform: translateX(4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .movie-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    min-width: 0;
  }

  .movie-header {
    flex: 1;
    align-items: center;
    margin-bottom: 0;
    gap: 16px;
    min-width: 0;
  }

  .title {
    font-size: 1.1rem;
    margin-right: 16px;
  }

  .action-buttons {
    gap: 12px;
    flex-shrink: 0;
  }
}

.movie-full {
  min-height: 350px;
  padding: 32px;
}

/* Enhanced movie header layout */
.movie-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 16px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* Enhanced typography and content styling */
.movie-title-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  margin: -24px -24px 0 -24px;
  border-radius: 16px 16px 0 0;
  position: relative;
  width: calc(100% + 48px);
  margin-bottom: 0;
  order: -1;

  &::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  }
}

.movie-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: white;
  line-height: 1.3;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: -0.025em;

  &:hover {
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    transform: translateY(-1px);
    transition: all 0.2s ease;
  }
}

.movie-card-content {
  background: white;
  border-radius: 0 0 16px 16px;
  padding: 24px;
  margin: -24px -24px -24px -24px;
  margin-top: 0;
  position: relative;
  display: flex;
  gap: 20px;
  align-items: flex-start;
  width: calc(100% + 48px);
}

.item-desc {
  color: #6b7280;
  font-weight: 500;
  font-size: 0.875rem;
  margin-right: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.details {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);

  > div {
    margin-bottom: 8px;
    font-size: 0.95rem;
    color: #4a5568;
    line-height: 1.5;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.details-minimal {
  background: transparent;
  padding: 0;
  margin-top: 0;
  border: none;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-shrink: 0;

  .release-date,
  .imdb-rating {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0;
    white-space: nowrap;
  }
}

.comment {
  margin-top: 16px;
  width: 100%;
  max-width: 500px;

  textarea {
    width: 100%;
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    padding: 12px;
    font-family: inherit;
    resize: vertical;
    min-height: 80px;
    transition: border-color 0.2s ease;

    &:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
  }

  button {
    margin-top: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
  }
}

.comment-readonly {
  background: rgba(248, 250, 252, 0.8);
  border-left: 4px solid #667eea;
  border-radius: 0 8px 8px 0;
  padding: 16px;
  margin-top: 12px;
  font-style: italic;
  color: #4a5568;
  line-height: 1.6;
}

.review {
  padding-top: 16px;

  button {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 8px 4px 8px 0;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: rgba(102, 126, 234, 0.2);
      transform: translateY(-1px);
    }
  }
}

.trailers {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;

  a {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s ease;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
  }
}

.urls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;

  a {
    transition: all 0.2s ease;
    border-radius: 6px;
    overflow: hidden;
    display: inline-block;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
  }

  .tmdb {
    background: url("/img/tmdb.svg");
    background-repeat: no-repeat;
    width: 70px;
    height: 50px;
    display: inline-block;
    background-size: contain;
    margin-left: 5px;
  }

  .imdb {
    background: url("/img/imdb.png");
    background-repeat: no-repeat;
    width: 104px;
    height: 50px;
    display: inline-block;
    background-size: contain;
  }
}

/* Enhanced provider and button styling */
.provider {
  width: 50px;
  height: 50px;
  margin: 4px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

.remove-button {
  display: flex;
  align-items: center;

  a {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    padding: 8px;
    border-radius: 6px;
    text-decoration: none;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;

    &:hover {
      background: rgba(239, 68, 68, 0.2);
      transform: translateY(-1px);
    }

    .v-icon {
      font-size: 16px;
    }
  }
}

.add-to-list-buttons {
  display: flex;
  align-items: center;

  a {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
    padding: 8px;
    border-radius: 6px;
    text-decoration: none;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;

    &:hover {
      background: rgba(34, 197, 94, 0.2);
      transform: translateY(-1px);
    }

    .v-icon {
      font-size: 16px;
    }
  }
}

.add-to-my-list-buttons {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;

  .v-btn {
    font-size: 0.75rem;
    padding: 4px 8px;
    height: auto;
    min-width: auto;
    border-radius: 6px;
    text-transform: none;
    font-weight: 500;

    .v-icon {
      font-size: 12px;
      margin-right: 2px;
    }
  }
}

.already-in-list {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  white-space: nowrap;

  .v-icon {
    font-size: 14px;
    margin-right: 4px;
  }
}

.review-minimal {
  padding-top: 8px;
  display: inline-flex;
  align-items: center;
  gap: 12px;

  .cancel-on-png,
  .cancel-off-png,
  .star-on-png,
  .star-off-png,
  .star-half-png {
    font-size: 1.16em;
  }

  .vue-star-rating {
    display: inline-flex;
    align-items: center;
  }
}

.details-minimal {
  display: inline;

  .release-date,
  .imdb-rating {
    float: right;
    margin-right: 10px;
  }
}

.form-control {
  width: auto;
}

/* New styles for add to list functionality */
.add-to-my-list-buttons {
  display: inline;
  margin-left: 10px;
}

.add-to-my-list-buttons .v-btn {
  margin-left: 5px;
  margin-right: 5px;
}

.already-in-list {
  display: inline-block;
  margin-left: 10px;
  font-size: 0.9em;
  color: #4caf50;
  align-items: center;
}

.gallery-add-buttons {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  padding: 5px;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-record:hover .gallery-add-buttons {
  opacity: 1;
}

.gallery-add-buttons .v-btn {
  margin: 2px;
  min-width: auto;
}

@media (max-width: 768px) {
  .search {
    margin-top: 10px;
  }

  .add-to-my-list-buttons .v-btn {
    font-size: 0.8em;
    padding: 4px 8px;
  }
}

@media (min-width: 320px) and (max-width: 576px) {
  .movie {
    max-width: 350px;
  }

  .review-minimal {
    .vue-star-rating {
      display: block;
      left: 0;
    }
  }

  .add-to-my-list-buttons {
    display: block;
    margin-top: 10px;
    margin-left: 0;
  }

  .gallery-add-buttons {
    position: static;
    opacity: 1;
    background: rgba(255, 255, 255, 0.95);
    margin-bottom: 5px;
  }
}

.results {
  clear: both;
  margin-top: 20px;
  padding: 0;
}

.add-to-list-buttons {
  display: inline;
  a,
  span {
    margin-left: 10px;
  }
}

.poster-big {
  width: 185px;
}

#movie-count {
  font-size: 25px;
  float: right;
  text-align: right;
  color: #707070;

  img {
    margin-top: 10px;
  }
}

@media (min-width: 320px) and (max-width: 576px) {
  #movie-count {
    float: none;
  }
}

.movie-count {
  display: inline;
  margin-left: 10px;
}

#gallery {
  margin: 0;
  padding: 12px;

  .gallery-record {
    display: inline-block;
    position: relative;
    margin: 8px;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;

    img {
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      transition: all 0.3s ease;

      &.draggable {
        cursor: grab;

        &:active {
          cursor: grabbing;
          transform: rotate(2deg);
        }
      }
    }

    button {
      opacity: 0;
      position: absolute;
      right: 12px;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(0, 0, 0, 0.1);
      border-radius: 8px;
      padding: 8px;
      transition: all 0.2s ease;
      cursor: pointer;

      &:hover {
        background: white;
        transform: scale(1.05);
      }

      .v-icon {
        color: #667eea;
        font-size: 18px;
      }
    }

    .up-button {
      bottom: 70px;
    }

    .down-button {
      bottom: 25px;
    }

    &:hover {
      transform: translateY(-4px);

      img {
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
        transform: scale(1.02);
      }

      button {
        opacity: 1;
      }
    }

    @media (max-width: 768px) {
      button {
        opacity: 1;
        background: rgba(255, 255, 255, 0.9);
      }
    }

    @media (min-width: 320px) and (max-width: 576px) {
      .poster-big {
        width: 92px;
      }

      .up-button {
        bottom: 50px;
      }

      .down-button {
        bottom: 15px;
      }

      button {
        padding: 6px;
        right: 8px;

        .v-icon {
          font-size: 16px;
        }
      }
    }
  }
}

/* Controls section styling */
.controls-section {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

/* Enhanced button toggle styling */
:deep(.v-btn-toggle) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px !important;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.05);

  .v-btn {
    border-radius: 8px !important;
    text-transform: none !important;
    font-weight: 500 !important;
    margin: 2px !important;
    transition: all 0.2s ease !important;
    color: #6c757d !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    &:hover {
      background: rgba(102, 126, 234, 0.1) !important;
      color: #667eea !important;
      transform: translateY(-1px);
    }

    &.v-btn--active {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      color: white !important;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }

    &.v-btn--size-small {
      font-size: 0.875rem !important;
      padding: 8px 12px !important;
    }

    &.v-btn--size-x-small {
      font-size: 0.75rem !important;
      padding: 6px 10px !important;
    }
  }
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .controls-section {
    padding: 16px;
    margin-bottom: 20px;
  }

  .control-group {
    gap: 6px;
  }

  .control-label {
    font-size: 0.8rem;
  }

  :deep(.v-btn-toggle) {
    padding: 2px;

    .v-btn {
      margin: 1px !important;
      font-size: 0.8rem !important;
      padding: 6px 8px !important;

      &.v-btn--size-small {
        font-size: 0.75rem !important;
        padding: 6px 8px !important;
      }

      &.v-btn--size-x-small {
        font-size: 0.7rem !important;
        padding: 4px 6px !important;
      }
    }
  }
}

@media (max-width: 480px) {
  .controls-section {
    padding: 12px;
    margin-bottom: 16px;
  }

  .control-label {
    font-size: 0.75rem;
  }
}

/* Movie layout responsive fixes */
@media (max-width: 768px) {
  .movie {
    flex-direction: column;
    gap: 16px;

    .poster {
      align-self: center;
    }

    .movie-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;

      .action-buttons {
        align-self: flex-end;
      }
    }
  }

  .movie-minimal {
    flex-direction: row;
    gap: 12px;

    .movie-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }

    .movie-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;

      .action-buttons {
        align-self: flex-start;
      }
    }

    .details-minimal {
      gap: 8px;

      .release-date,
      .imdb-rating {
        font-size: 0.75rem;
        padding: 3px 6px;
      }
    }
  }
}

@media (max-width: 480px) {
  .movie {
    padding: 16px;

    .poster {
      align-self: flex-start;
    }
  }

  .movie-minimal {
    padding: 12px 16px;

    .poster {
      display: none;
    }
  }
}

/* Enhanced website link styling */
.poster {
  position: relative;
  overflow: hidden;

  &:hover {
    .poster-overlay-buttons {
      opacity: 1;
    }
  }
}

.poster-overlay-buttons {
  position: absolute;
  right: 12px;
  bottom: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 6px;
  opacity: 0;
  transition: all 0.3s ease;
  display: flex;
  gap: 4px;
  z-index: 10;

  .remove-button a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    transition: all 0.2s ease;
    text-decoration: none;
    cursor: pointer;

    &:hover {
      background: rgba(239, 68, 68, 0.2);
      transform: scale(1.1);
    }

    &:active {
      transform: scale(0.95);
    }

    .v-icon {
      font-size: 16px;
      pointer-events: none;
    }
  }

  .add-to-list-buttons {
    display: flex;
    gap: 4px;

    a {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: rgba(34, 197, 94, 0.1);
      color: #22c55e;
      transition: all 0.2s ease;
      text-decoration: none;
      cursor: pointer;

      &:hover {
        background: rgba(34, 197, 94, 0.2);
        transform: scale(1.1);
      }

      &:active {
        transform: scale(0.95);
      }

      .v-icon {
        font-size: 16px;
        pointer-events: none;
      }
    }
  }

  .add-to-my-list-buttons {
    display: flex;
    flex-direction: column;
    gap: 2px;

    .v-btn {
      font-size: 0.6rem;
      padding: 2px 4px;
      min-width: auto;
      height: 24px;
    }

    .already-in-list {
      display: flex;
      align-items: center;
      gap: 2px;
      font-size: 0.65rem;
      color: #22c55e;
      padding: 2px 4px;
      background: rgba(34, 197, 94, 0.1);
      border-radius: 4px;
    }
  }
}

/* Touch device support */
@media (hover: none) and (pointer: coarse) {
  .poster-overlay-buttons {
    opacity: 1;
    background: rgba(255, 255, 255, 0.9);
  }
}

.urls {
  .website-link-container {
    margin-bottom: 8px;
  }
}

.website-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  text-decoration: none !important;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    color: white !important;
    text-decoration: none !important;
    background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  }

  &:focus {
    outline: 2px solid rgba(102, 126, 234, 0.5);
    outline-offset: 2px;
  }

  .website-icon {
    color: rgba(255, 255, 255, 0.9);
  }

  .external-icon {
    color: rgba(255, 255, 255, 0.7);
    margin-left: auto;
  }
}

@media (max-width: 768px) {
  .website-link {
    padding: 8px 12px;
    font-size: 0.85rem;
    gap: 6px;
  }
}
</style>
