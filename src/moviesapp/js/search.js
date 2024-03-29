'use strict';

import axios from 'axios';
import {initAxios} from './helpers';
import {newApp} from './app';
import MoviesList from './components/movies_list.js';

String.prototype.toTitleCase = function() { // eslint-disable-line no-extend-native
  return this.replace(/\w\S*/g, function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substring(1).toLowerCase();
  });
};

newApp({
  data() {
    const vars = window.vars;
    return {
      urls: window.urls,
      searchType: gettext('Movie'),
      searchTypeCode: 'movie',
      language: vars.language,
      query: '',
      movies: [],
      popularOnly: true,
      sortByDate: false,
    };
  },
  components: {
    MoviesList,
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
      const url = vm.urls.searchMovie;
      axios.get(url, {params: data}).then(function(response) {
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
    changeSearchType(code) {
      const vm = this;
      vm.searchTypeCode = code;
      vm.searchType = gettext(code.toTitleCase());
    },
  },
  mounted() {
    initAxios(this);
  },
}).mount('#app');
