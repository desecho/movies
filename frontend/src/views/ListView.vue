<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn-toggle v-model="mode" density="compact" mandatory>
          <v-btn value="full" :size="modeButtonSize">Full</v-btn>
          <v-btn value="compact" :size="modeButtonSize">Compact</v-btn>
          <v-btn value="minimal" :size="modeButtonSize">Minimal</v-btn>
          <v-btn value="gallery" :size="modeButtonSize">Gallery</v-btn>
        </v-btn-toggle>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-btn-toggle v-model="sort" density="compact" mandatory>
          <v-btn value="releaseDate" :size="sortButtonSize">Release date</v-btn>
          <v-btn value="rating" :size="sortButtonSize">Rating</v-btn>
          <v-btn value="additionDate" :size="sortButtonSize">Date added</v-btn>
          <v-btn v-if="listId == listToWatchId" value="custom" :size="sortButtonSize"> Custom </v-btn>
        </v-btn-toggle>
      </v-col>
    </v-row>
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
    </v-row>
    <v-row>
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
                <div class="title">
                  <span :title="element.movie.titleOriginal">{{ element.movie.title }}</span>
                  <div class="remove-button">
                    <a href="javascript:void(0)" title="Delete" @click="removeRecord(element, index)">
                      <v-icon icon="mdi-trash-can" />
                    </a>
                  </div>
                  <div class="add-to-list-buttons">
                    <div class="inline">
                      <div v-if="listId == listToWatchId" class="inline">
                        <a
                          v-show="element.movie.isReleased && element.listId != listWatchedId"
                          href="javascript:void(0)"
                          title='Add to "Watched" list'
                          @click="addToList(element.movie.id, listWatchedId, element)"
                        >
                          <v-icon icon="mdi-eye" />
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-show="mode != 'minimal'" class="poster">
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
                    <div v-show="element.movie.homepage">
                      <a :href="element.movie.homepage" target="_blank">Website</a>
                    </div>
                    <div class="urls">
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
                  <div v-if="listId == listWatchedId">
                    <star-rating
                      v-model:rating="element.rating"
                      :star-size="starSize"
                      :show-rating="false"
                      :clearable="true"
                      @update:rating="changeRating(element, $event)"
                    >
                    </star-rating>
                    <div v-show="(element.comment || element.commentArea) && mode != 'minimal'" class="comment">
                      <!-- {% if anothers_account %}
                    <p>{{ element.comment }}</p>
                  {% else %} -->
                      <div>
                        <v-textarea v-model="element.comment" class="form-control" title="Comment"> </v-textarea>
                      </div>
                      <button type="button" class="btn btn-secondary" title="Save" @click="saveComment(element)">
                        <v-icon icon="mdi-content-save" />
                      </button>
                    </div>
                    <button
                      v-show="element.comment == '' && !element.commentArea && mode != 'minimal'"
                      type="button"
                      class="btn btn-secondary"
                      title="Add comment"
                      @click="showCommentArea(element)"
                    >
                      <v-icon icon="mdi-comment" />
                    </button>
                    <div v-show="mode == 'full'" class="option-buttons">
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
            </template>
          </draggable>
        </div>
        <div v-cloak v-if="mode === 'gallery'" id="gallery">
          <draggable v-model="records" item-key="id" :disabled="!isSortable" @sort="saveRecordsOrder">
            <template #item="{ element, index }">
              <div v-if="paginatedRecords.includes(element)" class="gallery-record">
                <div class="buttons">
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
import type { AxiosError } from "axios";

import { useMobile } from "../composables/mobile";
import { listToWatchId, listWatchedId, starSizeMinimal, starSizeNormal } from "../const";
import { getSrcSet, getUrl } from "../helpers";
import { useRecordsStore } from "../stores/records";
import { $toast } from "../toast";

const props = defineProps<{
  listId: number;
}>();

const { isMobile } = useMobile();

const recordsStore = useRecordsStore();

const mode = ref("full");
const sort = ref("additionDate");
const query = ref("");
const records = toRef(recordsStore, "records");

const page = ref(1);
const perPage = 50;

const filteredRecords = computed(() => {
  const q = query.value.trim().toLowerCase();
  return records.value.filter((record) => {
    return (
      (record.movie.title.toLowerCase().includes(q) || record.movie.titleOriginal.toLowerCase().includes(q)) &&
      record.listId === props.listId
    );
  });
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
      if (props.listId === listWatchedId) {
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
watch(listIdRef, () => {
  sortRecords();
});

const starSize = computed(() => {
  if (mode.value === "minimal") {
    return starSizeMinimal;
  }
  return starSizeNormal;
});

const isSortable = computed(() => {
  return (
    props.listId === listToWatchId && sort.value === "custom" && (mode.value === "minimal" || mode.value === "gallery")
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

onMounted(() => {
  const { loadRecords } = useRecordsStore();
  loadRecords().catch((error: AxiosError) => {
    console.log(error);
    $toast.error("Error loading movies");
  });
});
</script>

<style src="@hennge/vue3-pagination/dist/vue3-pagination.css"></style>
<style scoped>
.option-buttons {
  input {
    margin-left: 5px;
  }
}

.poster {
  float: left;
  margin-right: 10px;
  margin-bottom: 10px;

  img {
    border-radius: 5px;
  }
}

.poster-small {
  width: 92px;
}

#query {
  text-align: right;
}

.movie {
  clear: both;
  min-height: 160px;
  margin-bottom: 10px;
  padding: 10px;
  border-width: 1px;
  border-style: solid;
  border-color: #ddd;
  border-radius: 4px;
}

.movie-minimal {
  min-height: 0;
  margin: 10px 0 0 0;
  padding: 0;
  border-width: 0 0 1px 0;
  border-radius: 0;
}

.movie-full {
  min-height: 300px;
}
.item-desc {
  color: #808080;
}

.comment {
  margin-top: 10px;
  width: 400px;
  textarea {
    display: inline;
  }
}

.review {
  padding-top: 10px;
  button {
    margin: 10px 0;
  }
}

.trailers a {
  margin-left: 10px;
}

.urls {
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

.provider {
  width: 50px;
  height: 50px;
  margin-left: 10px;
  border-radius: 5px;
}

.remove-button {
  display: inline;
  margin-left: 10px;
}

.review-minimal {
  padding-top: 0;
  display: inline;

  .cancel-on-png,
  .cancel-off-png,
  .star-on-png,
  .star-off-png,
  .star-half-png {
    font-size: 1.16em;
  }

  .vue-star-rating {
    display: inline;
    top: -2px;
    position: relative;
    left: 5px;
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

@media (max-width: 768px) {
  .search {
    margin-top: 10px;
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
}

.results {
  clear: both;
  margin-top: 20px;
  padding: 0;
}

.title {
  /* copied mostly from bootstrap h4 */
  font-size: 1em;
  font-weight: bold;
  line-height: 20px;
  display: inline;
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
  margin-left: 8px;

  .gallery-record {
    display: inline-block;
    position: relative;

    img {
      box-shadow:
        0 4px 8px 0 rgba(0, 0, 0, 0.2),
        0 6px 20px 0 rgba(0, 0, 0, 0.19);
      margin: 7px;
    }

    button {
      opacity: 0;
      position: absolute;
      right: 15px;
      background-color: white;
      border-radius: 5px;
    }

    .up-button {
      bottom: 60px;
    }

    .down-button {
      bottom: 20px;
    }

    &:hover {
      button {
        opacity: 0.7;
      }
    }

    @media (min-width: 320px) and (max-width: 576px) {
      .poster-big {
        width: 92px;
      }
    }
  }
}
</style>
