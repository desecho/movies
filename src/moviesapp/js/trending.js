'use strict';

import {newApp} from './app';
import {initAxios} from './helpers';
import MoviesList from './components/movies_list.js';

newApp({
  data() {
    const vars = window.vars;
    return {
      urls: window.urls,
      movies: vars.movies,
    };
  },
  components: {
    MoviesList,
  },
  mounted() {
    initAxios(this);
  },
}).mount('#app');
