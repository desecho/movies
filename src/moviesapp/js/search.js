'use strict';

import axios from 'axios';
import {retina, param} from './helpers';
import {newApp} from './app';

String.prototype.toTitleCase = function() { // eslint-disable-line no-extend-native
  return this.replace(/\w\S*/g, function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substring(1).toLowerCase();
  });
};

window.vm = newApp({
  data() {
    return {
      searchType: gettext('Movie'),
      searchTypeCode: 'movie',
      language: vars.language,
      query: '',
      movies: [],
      popularOnly: true,
      sortByDate: false,
      listWatchedId: vars.listWatchedId,
      listToWatchId: vars.listToWatchId,
    };
  },
  methods: {
    search() {
      const vm = this;
      const options = {
        popularOnly: vm.popularOnly,
        sortByDate: vm.sortByDate,
      };
      const data = {
        query: vm.query,
        type: vm.searchTypeCode,
        options: JSON.stringify(options),
      };
      const url = urls.searchMovie + '?' + param(data);
      axios.get(url).then(function(response) {
        const movies = response.data.movies;
        if (movies.length === 0) {
          vm.$toast.info(gettext('Nothing has been found'));
        }
        movies.forEach((m) => {
          m.hide = false;
        });
        vm.movies = movies;
      }).catch(function() {
        vm.$toast.error(gettext('Search Error'));
      });
    },
    retinajs: retina,
    addToListFromDb(movie, listId) {
      const vm = this;
      axios.post(urls.addToListFromDb, {
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
    changeSearchType(code) {
      const vm = this;
      vm.searchTypeCode = code;
      vm.searchType = gettext(code.toTitleCase());
    },
  }});

window.vm.mount('#app');
