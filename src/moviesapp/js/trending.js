'use strict';

import {newApp} from './app';
import {initAxios} from './helpers';
import MoviesList from './components/movies_list.js';

window.vm = newApp({
  data() {
    return {
      urls: vars.urls,
      movies: vars.movies,
    };
  },
  components: {
    MoviesList,
  },
  mounted() {
    initAxios(this);
  },
});

window.vm.mount('#app');
