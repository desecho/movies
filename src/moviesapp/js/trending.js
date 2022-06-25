'use strict';

import {newApp} from './app';
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
});

window.vm.mount('#app');
