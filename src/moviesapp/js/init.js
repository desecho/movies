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

if (vars.isVkApp) {
  $('.vk-app-show').show();
  $('#content').addClass('vk');
} else {
  $('.vk-app-hide').show();
}
