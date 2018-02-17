/* global VK:false */
/* global retinajs:false */

'use strict';

angular.module('app', ['ngResource', 'angular-loading-bar', 'ngCookies', 'angular-growl']);

const urls = {}; // eslint-disable-line no-unused-vars

(function() {
  angular.module('app').directive('instantRetina', function() {
    return {
      restrict: 'A',
      link: function(scope, element, attrs) {
        element.bind('load', function() {
          const el = angular.element(element);
          if (el.data('rjs-processed-2')) {
            return;
          }
          el.removeAttr('data-rjs-processed');
          // We need to remove height because retinajs apparently adds height attribute and it can't fix the
          // image after that
          el.removeAttr('height');
          el.attr('data-rjs-processed-2', true);
          retinajs();
        });
      },
    };
  });

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
      // I can't make $windowProvider to work.
      return window.self !== window.top; // eslint-disable-line angular/window-service
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
      return angular.element(this).data('rating');
    },
  };

  angular.module('app').constant('isVkApp', isVkApp);
  angular.module('app').constant('ratySettings', ratySettings);
  angular.module('app').controller('MenuController', MenuController);

  function MenuController() {
    const vm = this;
    vm.changeLanguage = changeLanguage;
    vm.invite = invite;

    function changeLanguage() {
      angular.element('#language-form').submit();
    }

    function invite() {
      VK.callMethod('showInviteBox');
    }
  }
})();

(function() {
  angular.module('app').factory('errorService', factory);
  factory.$inject = ['growl'];

  function factory(growl) {
    return {
      handleError: handleError,
    };

    function handleError(response, error) {
      if (response.status == 403) {
        growl.info(gettext('You need to login to add a movie to your list.'));
      } else {
        error();
      }
    }
  }
})();
