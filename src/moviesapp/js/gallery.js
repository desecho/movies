'use strict';

import Vue from 'vue';
import {
  retina,
} from './helpers';

window.vm = new Vue({
  el: '#app',
  methods: {
    openUrl: function(url) {
      location.href = url;
    },
    retinajs: retina,
  }
});
