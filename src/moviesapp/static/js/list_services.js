'use strict';

(function() {
  angular.module('app').factory('iconService', factory);

  function factory() {
    return {
      setViewedIconAndRemoveButtons: setViewedIconAndRemoveButtons,
    };

    function setViewedIconAndRemoveButtons(recordId, listId) {
      function removeButtons() {
        return angular.element('#record' + recordId).children('.title').children('.add-to-list-buttons').remove();
      }

      function setViewedIcon(recordId, listId) {
        let icon;
        let title;

        if (listId === 0) {
          return;
        } else if (listId === 1) {
          icon = '';
          title = gettext('Watched');
        } else if (listId === 2) {
          icon = '-slash';
          title = gettext('To Watch');
        }
        const html = ` <i class="fa fa-eye${icon}" title=${title}></i> `;
        return angular.element('#record' + recordId).children('.title').prepend(html);
      }

      setViewedIcon(recordId, listId);
      if (listId !== 0) {
        return removeButtons();
      }
    }
  }
})();

(function() {
  angular.module('app').factory('movieService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlAddToList + ':movieId/', {
      movieId: '@movieId',
    }, {
      add: {
        method: 'POST',
      },
    });
  }
})();

(function() {
  angular.module('app').factory('movieDataservice', factory);
  factory.$inject = ['movieService', 'growl', 'iconService', 'errorService'];

  function factory(movieService, growl, iconService, errorService) {
    return {
      add: addMovie,
    };

    function addMovie(movieId, listId, recordId) {
      return movieService.add({
        movieId: movieId,
      }, angular.element.param({
        listId: listId,
      }), success, fail);

      function success() {
        iconService.setViewedIconAndRemoveButtons(recordId, listId);
      }

      function error() {
        growl.error(gettext('Error adding the movie to the list'));
      }

      function fail(response) {
        errorService.handleError(response, error);
      }
    }
  }
})();
