'use strict';

$.jGrowl.defaults.closerTemplate = '<div>' + gettext('Close all notifications') + '</div>';

angular.module('app', ['ngResource', 'angular-loading-bar', 'ngCookies']);
angular.module('app').directive('ngEnter', function() {
  return function(scope, element, attrs) {
    element.bind('keydown keypress', function(event) {
      if (event.which === 13) {
        scope.$apply(function() {
          scope.$eval(attrs.ngEnter);
        });
        event.preventDefault();
      }
    });
  };
});

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
  config.$inject = ['$httpProvider', '$interpolateProvider', '$resourceProvider'];

  function config($httpProvider, $interpolateProvider, $resourceProvider) {
    $httpProvider.interceptors.push('appResourceInterceptor');
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    // Don't strip trailing slashes from calculated URLs
    $resourceProvider.defaults.stripTrailingSlashes = false;
  }

  angular.module('app').controller('MenuController', MenuController);

  function MenuController() {
    let vm = this;
    vm.changeLanguage = changeLanguage;
    function changeLanguage() {
      angular.element('#language-form').submit();
    }
  }
})();

let vars = {}; // eslint-disable-line no-unused-vars
let urls = {}; // eslint-disable-line no-unused-vars

function createPostResource(name, url) { // eslint-disable-line no-unused-vars
  angular.module('app').factory(name, factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(url, {}, {
      post: {
        method: 'POST',
      },
    });
  }
}

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

function displayMessage(message) {
  return $.jGrowl(message);
}

function handleError(error, errorFunc) { // eslint-disable-line no-unused-vars
  if (error.status == 403) {
    displayMessage(gettext('You need to login to add a movie to your list.'));
  } else {
    errorFunc();
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

if (!isVkUser) {
  $('.vk-app-hide').show();
}
$('#right-nav-bar').show();
