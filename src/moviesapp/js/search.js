'use strict';

import Vue from 'vue';
import axios from 'axios';
import {
  retina,
} from './helpers';


String.prototype.toTitleCase = function() { // eslint-disable-line no-extend-native
  return this.replace(/\w\S*/g, function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
};

window.vm = new Vue({
  el: '#app',
  data: {
    searchType: gettext('Movie'),
    searchTypeCode: 'movie',
    language: vars.language,
    query: '',
    movies: [],
    popularOnly: true,
    sortByDate: false,
  },
  methods: {
    search: function() {
      const options = {
        popularOnly: vm.popularOnly,
        sortByDate: vm.sortByDate,
      };
      const data = {
        query: vm.query,
        type: vm.searchTypeCode,
        options: JSON.stringify(options),
      };
      const url = urls.searchMovie + '?' + $.param(data);
      axios.get(url).then(function(response) {
        if (response.data.movies.length === 0) {
          vm.flashInfo(gettext('Nothing has been found'));
        }
        vm.movies = response.data.movies;
      }).catch(function() {
        vm.flashError(gettext('Search Error'));
      });
    },
    retinajs: retina,
    addToListFromDb: function(movieId, listId) {
      const movie = $('#movie' + movieId);
      axios.post(urls.addToListFromDb, {
        movieId: movieId,
        listId: listId,
      }).then(function(response) {
        if (response.data.status === 'not_found') {
          vm.flashError(gettext('Movie is not found in the database'));
          return;
        }
        movie.fadeOut('fast');
      }).catch(function() {
        vm.flashError(gettext('Error adding a movie'));
      });
    },
    changeSearchType: function(code) {
      vm.searchTypeCode = code;
      vm.searchType = gettext(code.toTitleCase());
    },
  },
});
