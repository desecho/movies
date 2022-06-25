'use strict';

import VueToast from 'vue-toast-notification';
import VueCookie from 'vue-cookies';
import {createApp} from 'vue';
import VLazyImage from 'v-lazy-image';
import draggable from 'vuedraggable';
import StarRating from 'vue-star-rating';

import {library} from '@fortawesome/fontawesome-svg-core';
/* import font awesome icon component */
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome';

/* import specific icons */
import {faGear, faSignIn, faSignOut, faEye, faEyeSlash, faTrash, faFilm, faEnvelopeOpen, faXmark, faShare, faSave,
  faComment, faArrowDown, faArrowUp} from '@fortawesome/free-solid-svg-icons';
import {faVk, faFacebook} from '@fortawesome/free-brands-svg-icons';

/* add icons to the library */
library.add(faGear, faSignIn, faSignOut, faEye, faEyeSlash, faTrash, faFilm, faEnvelopeOpen, faXmark,
    faShare, faSave, faComment, faVk, faFacebook, faArrowDown, faArrowUp);

export function newApp(options) {
  const app = createApp(options);
  app.config.compilerOptions.delimiters = ['[[', ']]'];
  app.use(VueToast, {
    position: 'top-right',
    duration: 1500,
  },
  );
  app.use(VueCookie);

  app.component('FontAwesomeIcon', FontAwesomeIcon);
  app.component('VLazyImage', VLazyImage);
  app.component('Draggable', draggable); // eslint-disable-line vue/multi-word-component-names
  app.component('StarRating', StarRating);

  return app;
}
