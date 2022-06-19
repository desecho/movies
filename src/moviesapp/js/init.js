/* global VK:false */

'use strict';

import Vue from 'vue';
import VueFlashMessage from 'vue-flash-message';
import VueCookie from 'vue-cookies';

import {library} from '@fortawesome/fontawesome-svg-core';
/* import font awesome icon component */
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome';

/* import specific icons */
import {faGear, faSignIn, faSignOut, faEye, faEyeSlash, faTrash, faFilm,
  faEnvelopeOpen, faXmark, faShare, faSave, faComment} from '@fortawesome/free-solid-svg-icons';
import {faVk, faFacebook} from '@fortawesome/free-brands-svg-icons';

/* add icons to the library */
library.add(faGear, faSignIn, faSignOut, faEye, faEyeSlash, faTrash, faFilm, faEnvelopeOpen, faXmark,
    faShare, faSave, faComment, faVk, faFacebook);

function getIsVkApp() {
  function inIframe() {
    try {
      return window.self !== window.top;
    } catch (e) {
      return true;
    }
  }

  if (vars.isVkUser) {
    return inIframe();
  }
  return false;
}

Vue.use(VueFlashMessage, {
  messageOptions: {
    timeout: 1500,
    important: true,
  },
});
Vue.use(VueCookie);
Vue.options.delimiters = ['[[', ']]'];
Vue.component('FontAwesomeIcon', FontAwesomeIcon);

new Vue({
  el: '#menu',
  methods: {
    changeLanguage: function() {
      $('#language-form').submit();
    },
    invite: function() {
      VK.callMethod('showInviteBox');
    },
  },
});

vars.isVkApp = getIsVkApp();
// Hardcode list IDs
vars.listWatchedId = 1;
vars.listToWatchId = 2;

if (vars.isVkApp) {
  $('.vk-app-show').show();
  $('#content').addClass('vk');
} else {
  $('.vk-app-hide').show();
}

vars.ratySettings = {
  hints: [
    gettext('Awful'),
    gettext('Bad'),
    gettext('Regular'),
    gettext('Good'),
    gettext('Awesome'),
  ],
  cancelHint: gettext('Cancel rating'),
  noRatedMsg: gettext('No rating yet'),
  cancel: true,
  starType: 'i',
  score: function() {
    return $(this).data('rating');
  },
};
