'use strict';

import Vue from 'vue';
import axios from 'axios';
import {
  retina,
} from './helpers';


String.prototype.toTitleCase = function() { // eslint-disable-line no-extend-native
  return this.replace(/\w\S*/g, function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substring(1).toLowerCase();
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
        const movies = response.data.movies;
        if (movies.length === 0) {
          vm.flashInfo(gettext('Nothing has been found'));
        }
        movies.forEach((m) => {
          m.hide = false;
        });
        vm.movies = movies;
      }).catch(function() {
        vm.flashError(gettext('Search Error'));
      });
    },
    retinajs: retina,
    addToListFromDb: function(movie, listId) {
      axios.post(urls.addToListFromDb, {
        movieId: movie.id,
        listId: listId,
      }).then(function(response) {
        if (response.data.status === 'not_found') {
          vm.flashError(gettext('Movie is not found in the database'));
          return;
        }
        movie.hide = true;
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
