/* global VK:false */

'use strict';

import Vue from 'vue';
import VueFlashMessage from 'vue-flash-message';
import VueCookie from 'vue-cookies';

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


vars.flashOptions = {
  timeout: 1500,
  important: true,
};
window.urls = {};

Vue.use(VueFlashMessage);
Vue.use(VueCookie);
Vue.options.delimiters = ['[[', ']]'];

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
