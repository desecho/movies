/* global VK:false */

'use strict';

import {newApp} from './app';

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

newApp({
  methods: {
    changeLanguage() {
      document.getElementById('language-form').submit();
    },
    invite() {
      VK.callMethod('showInviteBox');
    },
  },
}).mount('#menu');

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
