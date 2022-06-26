'use strict';

import {newApp} from './app';

newApp({
  methods: {
    changeLanguage() {
      document.getElementById('language-form').submit();
    },

  },
}).mount('#menu');
