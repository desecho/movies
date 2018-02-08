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

$.jGrowl.defaults.closerTemplate = '<div>' + gettext('Close all notifications') + '</div>';

const headers = { // eslint-disable-line no-unused-vars
  'X-CSRFToken': csrftoken,
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'X-Requested-With': 'XMLHttpRequest',
};

const app = angular.module('movies', ['ngResource', 'angular-loading-bar']);
app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});
app.config(['$resourceProvider', function($resourceProvider) {
  // Don't strip trailing slashes from calculated URLs
  $resourceProvider.defaults.stripTrailingSlashes = false;
}]);

if (!isVkUser) {
  $('.vk-app-hide').show();
}
$('#right-nav-bar').show();
