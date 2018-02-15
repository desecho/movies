'use strict';

String.prototype.toTitleCase = function() { // eslint-disable-line no-extend-native
  return this.replace(/\w\S*/g, function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
};

(function() {
  angular.module('app').factory('moviesService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlSearchMovie, {}, {
      search: {
        method: 'GET',
      },
    });
  }
})();

(function() {
  angular.module('app').factory('moviesDataservice', factory);
  factory.$inject = ['moviesService', 'growl'];

  function factory(moviesService, growl) {
    return {
      search: search,
    };

    function search(data) {
      return moviesService.search(data, success, fail);

      function success(response) {
        if (response.movies.length === 0) {
          growl.info(gettext('Nothing has been found'));
        }
      }

      function fail() {
        growl.error(gettext('Search Error'));
      }
    }
  }
})();

(function() {
  angular.module('app').factory('addToListFromDbService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlAddToListFromDb, {}, {
      add: {
        method: 'POST',
      },
    });
  }
})();

(function() {
  angular.module('app').factory('addToListFromDbDataservice', factory);
  factory.$inject = ['addToListFromDbService', 'growl', 'errorService'];

  function factory(addToListFromDbService, growl, errorService) {
    return {
      add: add,
    };

    function add(data) {
      return addToListFromDbService.add(angular.element.param(data), success, fail);

      function success(response) {
        if (response.status === 'not_found') {
          return growl.error(gettext('Movie is not found in the database'));
        }
      }

      function error() {
        growl.error(gettext('Error adding a movie'));
      }

      function fail(response) {
        errorService.handleError(response, error);
      }
    }
  }
})();

(function() {
  angular.module('app').controller('MoviesSearchController', MoviesSearchController);
  MoviesSearchController.$inject = ['moviesDataservice', 'addToListFromDbDataservice'];

  function MoviesSearchController(moviesDataservice, addToListFromDbDataservice) {
    const vm = this;
    vm.searchType = gettext('Movie');
    vm.searchTypeCode = 'movie';
    vm.search = search;
    vm.addToListFromDb = addToListFromDb;
    vm.changeSearchType = changeSearchType;

    function search() {
      vm.nothingFound = false;
      vm.movies = [];
      const options = {
        popularOnly: angular.element('#popular-only').prop('checked'),
        sortByDate: angular.element('#sort-by-date').prop('checked'),
      };
      moviesDataservice.search({
        query: vm.query,
        type: vm.searchTypeCode,
        options: angular.element.param(options),
      }).$promise.then(function(response) {
        if (response.status === 'success') {
          vm.movies = response.movies;
        }
      }).catch(function() {});
    }

    function addToListFromDb(movieId, listId) {
      let movie = angular.element('#movie' + movieId);
      movie.fadeOut('fast');
      addToListFromDbDataservice.add({
        movieId: movieId,
        listId: listId,
      }).$promise.catch(function() {});
    }

    function changeSearchType(code) {
      vm.searchTypeCode = code;
      vm.searchType = gettext(code.toTitleCase());
    }
  }
})();
