'use strict';

import Vue from 'vue';
import {
  retina,
} from './helpers';
import {
  addToList,
} from './list_helpers';


window.vm = new Vue({
  el: '#app',
  data: {
    listWatchedId: vars.listWatchedId,
    listToWatchId: vars.listToWatchId,
  },
  methods: {
    retinajs: retina,
    addToList: addToList,
  },
});

const settings = $.extend({
  readOnly: true,
}, vars.ratySettings);
$('.rating').raty(settings);
