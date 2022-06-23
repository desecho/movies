'use strict';

import {newApp} from './app';
import {retina, getSrcSet} from './helpers';


window.vm = newApp({
  data() {
    return {
      movies: vars.movies,
      listWatchedId: vars.listWatchedId,
      listToWatchId: vars.listToWatchId,
      listId: vars.listId,
      urlGalleryWatched: vars.urlGalleryWatched,
      urlGalleryToWatch: vars.urlGalleryToWatch,
    };
  },
  methods: {
    openUrl(url) {
      location.href = url;
    },
    getSrcSet: getSrcSet,
    retinajs: retina,
  },
});

window.vm.mount('#app');
