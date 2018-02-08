/* global urlSearchMovie:false */
/* global urlAddToListFromDb:false */

String.prototype.toTitleCase = function() { // eslint-disable-line no-extend-native
  return this.replace(/\w\S*/g, function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
};

app.factory('SearchMovie', ['$resource', function($resource) {
  return $resource(urlSearchMovie, {}, {
    get: {
      method: 'GET'
    },
  });
}]);

app.factory('AddToListFromDb', ['$resource', function($resource) {
  return $resource(urlAddToListFromDb, {}, {
    post: {
      method: 'POST',
      headers: headers
    },
  });
}]);

app.controller('MoviesSearchController', ['$scope', 'SearchMovie', 'AddToListFromDb',

  function($scope, SearchMovie, AddToListFromDb) {
    $scope.searchType = gettext('Movie');
    $scope.searchTypeCode = 'movie';
    $scope.submit = function() {
      function showError() {
        displayMessage(gettext('Search Error'));
      }
      $scope.nothingFound = false;
      $scope.searchResults = [];
      const options = {
        popularOnly: $('#popular-only').prop('checked'),
        sortByDate: $('#sort-by-date').prop('checked'),
      };
      SearchMovie.get({
        query: $scope.query,
        type: $scope.searchTypeCode,
        options: $.param(options),
      }, function(response) {
        if (response.status === 'success') {
          $scope.searchResults = response.movies;
          // It is not working without the timeout.
          setTimeout(function() {
            $('.poster img').removeAttr('data-rjs-processed');
            retinajs();
          }, 500);
        } else if (response.status === 'not_found') {
          $scope.nothingFound = true;
        } else {
          showError();
        }
      }, function() {
        showError();
      });
    };

    $scope.addToListFromDb = function(movieId, listId) {
      function showError() {
        displayMessage(gettext('Error adding a movie'));
      }

      let movie = $('#movie' + movieId);
      movie.fadeOut('fast');
      AddToListFromDb.post($.param({
        movieId: movieId,
        listId: listId,
      }), function(response) {
        if (response.status === 'success') {
          return;
        }
        movie.fadeIn('fast');
        if (response.status === 'not_found') {
          return displayMessage(gettext('Movie is not found in the database'));
        } else {
          showError();
        }
      }, function(error) {
        movie.fadeIn('fast');
        handleError(error, showError);
      });
    };

    $scope.changeSearchType = function(code) {
      $scope.searchTypeCode = code;
      $scope.searchType = gettext(code.toTitleCase());
    };
  }
]);

$('#search').show();
