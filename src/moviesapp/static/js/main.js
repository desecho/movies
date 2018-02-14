'use strict';

angular.module('app', ['ngResource', 'angular-loading-bar', 'ngCookies', 'angular-growl']);

const hints = [
  gettext('Awful'),
  gettext('Bad'),
  gettext('Regular'),
  gettext('Good'),
  gettext('Awesome'),
];

(function() {
  angular.module('app').factory('appResourceInterceptor', appResourceInterceptor);
  appResourceInterceptor.$inject = ['$cookies'];

  function appResourceInterceptor($cookies) {
    return {
      request: function(config) {
        const headers = {
          'X-CSRFToken': $cookies.get('csrftoken'),
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'X-Requested-With': 'XMLHttpRequest',
        };
        angular.extend(config.headers, headers);
        return config;
      },
    };
  }

  angular.module('app').config(config);

  config.$inject = ['$httpProvider', '$interpolateProvider', '$resourceProvider', 'growlProvider'];

  function config($httpProvider, $interpolateProvider, $resourceProvider, growlProvider) {
    $httpProvider.interceptors.push('appResourceInterceptor');
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');

    // Don't strip trailing slashes from calculated URLs
    $resourceProvider.defaults.stripTrailingSlashes = false;

    growlProvider.globalTimeToLive(2000);
    growlProvider.globalDisableCountDown(true);
    growlProvider.globalDisableIcons(true);
  }

  function inIframe() {
    try {
      return window.self !== window.top;
    } catch (e) {
      return true;
    }
  }
  let isVkApp = {};
  if (vars.isVkUser) {
    isVkApp = inIframe();
  } else {
    isVkApp = false;
  }
  if (isVkApp) {
    angular.element('.vk-app-show').show();
    angular.element('#content').addClass('vk');
  } else {
    angular.element('.vk-app-hide').show();
  }

  const ratySettings = {
    hints: hints,
    cancelHint: gettext('Cancel rating'),
    noRatedMsg: gettext('No rating yet'),
    cancel: true,
    starType: 'i',
    score: function() {
      return angular.element(this).data('rating');
    },
  };

  angular.module('app').constant('isVkApp', isVkApp);
  angular.module('app').constant('ratySettings', ratySettings);
  angular.module('app').controller('MenuController', MenuController);

  function MenuController() {
    const vm = this;
    vm.changeLanguage = changeLanguage;

    function changeLanguage() {
      angular.element('#language-form').submit();
    }
  }
})();

const urls = {}; // eslint-disable-line no-unused-vars

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie != '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function displayMessage(x) {
  alert(x);
}

function handleError(response, error) { // eslint-disable-line no-unused-vars
  if (response.status == 403) {
    displayMessage(gettext('You need to login to add a movie to your list.'));
  } else {
    error();
  }
}

const csrftoken = getCookie('csrftoken');

$.ajaxSetup({
  crossDomain: false, // obviate need for sameOrigin test
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type)) {
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
    }
  },
});

const headers = { // eslint-disable-line no-unused-vars
  'X-CSRFToken': csrftoken,
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'X-Requested-With': 'XMLHttpRequest',
};
