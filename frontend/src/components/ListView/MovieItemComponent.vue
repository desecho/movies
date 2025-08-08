<template>
  <div
    class="movie"
    :class="{
      'movie-minimal': mode == 'minimal',
      'movie-full': mode == 'full',
      draggable: isSortable,
    }"
  >
    <!-- Movie title banner spanning full width at the very top -->
    <div class="movie-title-banner">
      <h2 class="movie-title" :title="record.movie.titleOriginal">
        {{ record.movie.title }}
      </h2>
      <!-- Action buttons in title banner -->
      <div class="title-action-buttons">
        <!-- Only show action buttons for own lists -->
        <div v-if="!isProfileView" class="remove-button">
          <a href="javascript:void(0)" title="Delete" @click="$emit('remove', record, recordIndex)">
            <v-icon icon="mdi-trash-can" />
          </a>
        </div>
        <!-- Add to list buttons - show for logged in users viewing profile -->
        <div v-if="isProfileView && isLoggedIn" class="add-to-my-list-buttons">
          <v-btn
            v-if="!isMovieInMyList(record.movie.id)"
            size="x-small"
            color="primary"
            variant="outlined"
            title="Add to my Watched list"
            @click="$emit('add-to-my-list', record.movie.id, listWatchedId)"
          >
            <v-icon icon="mdi-eye" />
          </v-btn>
          <v-btn
            v-if="!isMovieInMyList(record.movie.id)"
            size="x-small"
            color="secondary"
            variant="outlined"
            title="Add to my To Watch list"
            @click="$emit('add-to-my-list', record.movie.id, listToWatchId)"
          >
            <v-icon icon="mdi-eye-off" />
          </v-btn>
          <span v-if="isMovieInMyList(record.movie.id)" class="already-in-list">
            <v-icon icon="mdi-check" color="success" />
            In your list
          </span>
        </div>
        <div v-if="!isProfileView" class="add-to-list-buttons">
          <div v-if="currentListId == listToWatchId">
            <a
              v-show="record.movie.isReleased && record.listId != listWatchedId"
              href="javascript:void(0)"
              title='Add to "Watched" list'
              @click="$emit('add-to-list', record.movie.id, listWatchedId, record)"
            >
              <v-icon icon="mdi-eye" />
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Movie card content below title -->
    <div class="movie-card-content">
      <div v-show="mode != 'minimal'" class="poster">
        <span v-if="mode == 'full'">
          <v-lazy-image
            class="poster-big"
            :srcset="getSrcSet(record.movie.posterNormal, record.movie.posterBig)"
            :src="record.movie.posterBig"
            :title="record.movie.titleOriginal"
            :alt="record.movie.title"
          />
        </span>
        <span v-else>
          <v-lazy-image
            class="poster-small"
            :srcset="getSrcSet(record.movie.posterSmall, record.movie.posterNormal)"
            :src="record.movie.posterNormal"
            :title="record.movie.titleOriginal"
            :alt="record.movie.title"
          />
        </span>
        <!-- Star rating under poster -->
        <div v-if="currentListId == listWatchedId" class="poster-rating">
          <star-rating
            :key="`rating-${record.id}-${record.rating}`"
            :rating="record.rating"
            :star-size="starSize"
            :show-rating="false"
            :clearable="!isProfileView"
            :read-only="isProfileView"
            @rating-selected="$emit('rating-changed', record, $event)"
          >
          </star-rating>
        </div>
      </div>
      <div
        class="details"
        :class="{
          'details-minimal': mode == 'minimal',
        }"
      >
        <div v-show="record.movie.imdbRating" class="imdb-rating">
          <span class="item-desc">IMDb Rating:</span>
          {{ record.movie.imdbRating }} ({{ record.movie.imdbRatingConverted }})
        </div>
        <div v-show="record.movie.isReleased" class="release-date">
          <span v-show="mode != 'minimal'" class="item-desc">Release Date:</span>
          {{ record.movie.releaseDate }}
        </div>
        <div v-show="mode == 'full'">
          <div v-show="record.movie.country">
            <span class="item-desc">Country:</span>
            {{ record.movie.country }}
          </div>
          <div v-show="record.movie.director">
            <span class="item-desc">Director:</span>
            {{ record.movie.director }}
          </div>
          <div v-show="record.movie.writer">
            <span class="item-desc">Writer:</span>
            {{ record.movie.writer }}
          </div>
          <div v-show="record.movie.genre">
            <span class="item-desc">Genre:</span>
            {{ record.movie.genre }}
          </div>
          <div v-show="record.movie.actors">
            <span class="item-desc">Actors:</span>
            {{ record.movie.actors }}
          </div>
          <div v-show="record.movie.runtime">
            <span class="item-desc">Runtime:</span>
            {{ record.movie.runtime }}
          </div>
          <div v-show="record.movie.overview">
            <span class="item-desc">Overview:</span>
            {{ record.movie.overview }}
          </div>
          <div class="urls">
            <div v-show="record.movie.homepage" class="website-link-container">
              <a :href="record.movie.homepage" target="_blank" class="website-link">
                <v-icon icon="mdi-web" size="small" class="website-icon" />
                Website
                <v-icon icon="mdi-open-in-new" size="x-small" class="external-icon" />
              </a>
            </div>
            <a :href="record.movie.imdbUrl" target="_blank"><span class="imdb"></span></a>
            <a :href="record.movie.tmdbUrl" target="_blank"><span class="tmdb"></span></a>
          </div>
          <div v-show="record.movie.trailers.length">
            <span class="item-desc">Trailers:</span>
            <div class="trailers">
              <a
                v-for="trailer in record.movie.trailers"
                :key="trailer.name"
                :href="trailer.url"
                target="_blank"
                >{{ trailer.name }}</a
              >
            </div>
          </div>
          <div v-show="record.providerRecords.length">
            <span class="item-desc">Stream on:</span>
            <div>
              <a
                v-for="providerRecord in record.providerRecords"
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
          <!-- Only show comment editing for own lists -->
          <div
            v-if="!isProfileView"
            v-show="(record.comment || record.commentArea) && mode != 'minimal'"
            class="comment"
          >
            <div>
              <v-textarea 
                :model-value="record.comment" 
                class="form-control" 
                title="Comment"
                @update:model-value="updateComment($event)"
              > </v-textarea>
            </div>
            <button type="button" class="btn btn-secondary" title="Save" @click="$emit('save-comment', record)">
              <v-icon icon="mdi-content-save" />
            </button>
          </div>
          <!-- Show comments read-only for profile views -->
          <div v-if="isProfileView && record.comment && mode != 'minimal'" class="comment-readonly">
            <p>{{ record.comment }}</p>
          </div>
          <button
            v-if="!isProfileView"
            v-show="record.comment == '' && !record.commentArea && mode != 'minimal'"
            type="button"
            class="btn btn-secondary"
            title="Add comment"
            @click="$emit('show-comment-area', record)"
          >
            <v-icon icon="mdi-comment" />
          </button>
          <!-- Only show options for own lists -->
          <div v-if="!isProfileView" v-show="mode == 'full'" class="option-buttons">
            <div>
              <label :for="'original_' + record.id">Watched original version</label>
              <input
                :id="'original_' + record.id"
                v-model="record.options.original"
                type="checkbox"
                @change="$emit('save-options', record, 'original')"
              />
            </div>
            <div>
              <label :for="'extended_' + record.id">Watched extended version</label>
              <input
                :id="'extended_' + record.id"
                v-model="record.options.extended"
                type="checkbox"
                @change="$emit('save-options', record, 'extended')"
              />
            </div>
            <div>
              <label :for="'theatre_' + record.id">Watched in theatre</label>
              <input
                :id="'theatre_' + record.id"
                v-model="record.options.theatre"
                type="checkbox"
                @change="$emit('save-options', record, 'theatre')"
              />
            </div>
            <div>
              <label :for="'hd_' + record.id">Watched in HD</label>
              <input
                :id="'hd_' + record.id"
                v-model="record.options.hd"
                type="checkbox"
                @change="$emit('save-options', record, 'hd')"
              />
            </div>
            <div>
              <label :for="'full_hd_' + record.id">Watched in FullHD</label>
              <input
                :id="'full_hd_' + record.id"
                v-model="record.options.fullHd"
                type="checkbox"
                @change="$emit('save-options', record, 'fullHd')"
              />
            </div>
            <div>
              <label :for="'4k_' + record.id">Watched in 4K</label>
              <input
                :id="'4k_' + record.id"
                v-model="record.options.ultraHd"
                type="checkbox"
                @change="$emit('save-options', record, 'ultraHd')"
              />
            </div>
            <div>
              <label :for="'ignoreRewatch_' + record.id">Ignore rewatch filter</label>
              <input
                :id="'ignoreRewatch_' + record.id"
                v-model="record.options.ignoreRewatch"
                type="checkbox"
                @change="$emit('save-options', record, 'ignoreRewatch')"
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

<script lang="ts" setup>
import { computed } from "vue";
import VLazyImage from "v-lazy-image";
import StarRating from "vue-star-rating";
import type { RecordType } from "../../types";
import { getSrcSet } from "../../helpers";
import { listToWatchId, listWatchedId, starSizeMinimal, starSizeNormal } from "../../const";

interface Props {
  record: RecordType;
  recordIndex: number;
  mode: string;
  currentListId: number;
  isProfileView: boolean;
  isSortable: boolean;
  isLoggedIn: boolean;
  myRecords?: RecordType[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "remove": [record: RecordType, index: number];
  "add-to-my-list": [movieId: number, listId: number];
  "add-to-list": [movieId: number, listId: number, record: RecordType];
  "rating-changed": [record: RecordType, rating: number];
  "save-comment": [record: RecordType];
  "show-comment-area": [record: RecordType];
  "save-options": [record: RecordType, field: keyof RecordType["options"]];
  "update-comment": [record: RecordType, comment: string];
}>();

const starSize = computed(() => {
  if (props.mode === "minimal") {
    return starSizeMinimal;
  }
  return starSizeNormal;
});

// Check if a movie is already in user's list
function isMovieInMyList(movieId: number): boolean {
  if (!props.isProfileView || !props.isLoggedIn || !props.myRecords?.length) {
    return false;
  }
  return props.myRecords.some((record) => record.movie.id === movieId);
}

function updateComment(comment: string): void {
  emit("update-comment", props.record, comment);
}
</script>

<style scoped>
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
  padding: 22px;
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
  display: flex;
  align-items: center;
  justify-content: space-between;

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

.title-action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;

  .remove-button a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.15);
    color: white;
    transition: all 0.2s ease;
    text-decoration: none;
    cursor: pointer;

    &:hover {
      background: rgba(255, 255, 255, 0.25);
      transform: scale(1.1);
    }

    .v-icon {
      font-size: 16px;
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
      background: rgba(255, 255, 255, 0.15);
      color: white;
      transition: all 0.2s ease;
      text-decoration: none;
      cursor: pointer;

      &:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: scale(1.1);
      }

      .v-icon {
        font-size: 16px;
      }
    }
  }

  .add-to-my-list-buttons {
    display: flex;
    flex-direction: row;
    gap: 4px;

    .v-btn {
      font-size: 0.7rem;
      padding: 2px 6px;
      min-width: auto;
      height: 28px;
      border-color: rgba(255, 255, 255, 0.3);
      color: white;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }
    }

    .already-in-list {
      display: flex;
      align-items: center;
      gap: 2px;
      font-size: 0.7rem;
      color: white;
      padding: 2px 6px;
      background: rgba(255, 255, 255, 0.15);
      border-radius: 4px;
    }
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

@media (max-width: 768px) {
  .movie-card-content {
    flex-direction: column;
    gap: 16px;
    align-items: center;
  }
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
  flex: 2;
  min-width: 600px;

  > div {
    font-size: 0.95rem;
    color: #4a5568;
    line-height: 1.5;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

@media (max-width: 768px) {
  .details {
    width: 100%;
    padding: 12px;
    min-width: auto;
    flex: 1;
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

.poster-big {
  width: 185px;
}

/* Poster Rating Styling */
.poster-rating {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.poster .poster-rating .vue-star-rating {
  display: flex;
  justify-content: center;
  align-items: center;
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
  width: 670px;
  max-width: 100%;

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

@media (max-width: 768px) {
  .review {
    width: 100%;
    padding-top: 12px;
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

.option-buttons {
  input {
    margin-left: 5px;
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

.form-control {
  width: auto;
}

/* Mobile responsive adjustments */
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

  .movie-full {
    padding: 18px;

    .movie-card-content {
      padding: 18px;

      .poster {
        align-self: center;
        margin-bottom: 16px;
      }

      .details {
        order: 1;
      }

      .review {
        order: 2;
        align-self: stretch;
      }
    }

    .movie-title-banner {
      padding: 16px 18px;
      margin: -18px -18px 0 -18px;
      width: calc(100% + 36px);
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;

      .movie-title {
        font-size: 1.5rem;
      }

      .title-action-buttons {
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

  .movie-full {
    padding: 14px;

    .movie-card-content {
      padding: 14px;
    }

    .movie-title-banner {
      padding: 14px;
      margin: -14px -14px 0 -14px;
      width: calc(100% + 28px);

      .movie-title {
        font-size: 1.3rem;
        line-height: 1.2;
      }

      .title-action-buttons {
        gap: 6px;

        .remove-button a,
        .add-to-list-buttons a {
          width: 28px;
          height: 28px;

          .v-icon {
            font-size: 14px;
          }
        }
      }
    }
  }

  .movie-minimal {
    padding: 12px 16px;

    .poster {
      display: none;
    }
  }
}
</style>