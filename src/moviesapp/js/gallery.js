'use strict';

import {newApp} from './app';
import {retina} from './helpers';


window.vm = newApp({
  methods: {
    openUrl(url) {
      location.href = url;
    },
    retinajs: retina,
  },
});

window.vm.mount('#app');
