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
        options: $.param(options),
      };
      const url = urls.urlSearchMovie + '?' + $.param(data);
      axios.get(url).then(function(response) {
        if (response.data.movies.length === 0) {
          vm.flash(gettext('Nothing has been found'), 'info', vars.flashOptions);
        }
        vm.movies = response.data.movies;
      }).catch(function() {
        vm.flash(gettext('Search Error'), 'error', vars.flashOptions);
      });
    },
    retinajs: retina,
    addToListFromDb: function(movieId, listId) {
      const movie = $('#movie' + movieId);
      movie.fadeOut('fast');
      const data = {
        movieId: movieId,
        listId: listId,
      };
      axios.post(urls.urlAddToListFromDb, $.param(data)).then(function(response) {
        if (response.data.status === 'not_found') {
          vm.flash(gettext('Movie is not found in the database'), 'error', vars.flashOptions);
        }
      }).catch(function() {
        vm.flash(gettext('Error adding a movie'), 'error', vars.flashOptions);
      });
    },
    changeSearchType: function(code) {
      vm.searchTypeCode = code;
      vm.searchType = gettext(code.toTitleCase());
    },
  },
});
