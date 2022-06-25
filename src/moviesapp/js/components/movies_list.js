'use strict';

import {listWatchedId, listToWatchId} from '../constants';
import {getSrcSet} from '../helpers';
import axios from 'axios';

const template = `
<div class="results" id="movies-list">
<div class="movie" v-show="!movie.hide" v-for="movie in movies">
  <div class="poster-wrapper">
    <div class="poster">
      <div class="add-to-list-buttons">
        <a
          href="javascript:void(0)"
          @click="addToListFromDb(movie, listWatchedId)"
          title="{% translate 'Add to the list' %} {% translate 'Watched' %}"
          v-show="movie.isReleased"
        >
          <font-awesome-icon icon="fa-solid fa-eye" />
        </a>
        <a href="javascript:void(0)" title="{% translate 'Add to the list' %} {% translate 'To Watch' %}"
          @click="addToListFromDb(movie, listToWatchId)"><font-awesome-icon icon="fa-solid fa-eye-slash" /></a>
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
    <div class="title">[[ movie.title ]]</div>
    <div class="details" v-show="movie.releaseDate">
      [[ movie.releaseDate ]]
    </div>
  </div>
</div>
</div>
`;

export default {
  props: {
    movies: Object,
    urls: Object,
  },
  data() {
    return {
      listWatchedId: listWatchedId,
      listToWatchId: listToWatchId,
    };
  },
  methods: {
    getSrcSet: getSrcSet,
    addToListFromDb(movie, listId) {
      const vm = this;

      axios.post(vm.urls.addToListFromDb, {
        movieId: movie.id,
        listId: listId,
      }).then(function(response) {
        if (response.data.status === 'not_found') {
          vm.$toast.error(gettext('Movie is not found in the database'));
          return;
        }
        movie.hide = true;
      }).catch(function() {
        vm.$toast.error(gettext('Error adding a movie'));
      });
    },
  },
  template: template,
};
