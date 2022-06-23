'use strict';

import {newApp} from './app';
import {retina} from './helpers';

const settings = $.extend({
  readOnly: true,
}, vars.ratySettings);
$('.rating').raty(settings);

newApp({
  methods: {
    retinajs: retina,
  },
}).mount('#app');
