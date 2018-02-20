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
  methods: {
    retinajs: retina,
    addToList: addToList,
  },
});

const settings = $.extend({
  readOnly: true,
}, vars.ratySettings);
$('.rating').raty(settings);
