'use strict';

import {newApp} from './app';

import {retina} from './helpers';

newApp(
    {methods: {
      retinajs: retina,
    },
    },
).mount('#app');
