app.factory('SearchMovie', ['$resource', function($resource) {
  return $resource(urlSearchMovie, {}, {
    get: {method: 'GET'}
  });
}]);

app.factory('AddToListFromDb', ['$resource', function($resource) {
  return $resource(urlAddToListFromDb, {}, {
    post: {method: 'POST', headers: headers}
  });
}]);

app.controller('MoviesSearchController', ['$scope', 'SearchMovie', 'AddToListFromDb',

function ($scope, SearchMovie, AddToListFromDb) {
  $scope.searchType = gettext('Movie');
  $scope.searchTypeId = 1;
  $scope.submit = function(){
    $scope.searchResults = [];
    const options = {
      popularOnly: $('#popular-only').prop('checked'),
      sortByDate: $('#sort-by-date').prop('checked')
    };
    SearchMovie.get({
      query: $scope.query,
      type: $scope.searchTypeId.toString(),
      options: $.param(options)
    }, function(data) {
      $scope.nothingFound = false;
      if (data.status === 1) {
        $scope.searchResults = data.movies;
      } else if (data.status === 0) {
        $scope.nothingFound = true;
      } else {
        displayMessage(gettext('Search Error'));
      }
    }, function(){displayMessage(gettext('Search Error'))}
    );
  }

  $scope.addToListFromDb = function(movieId, listId) {
    AddToListFromDb.post($.param({
      movieId: movieId,
      listId: listId
    }), function(data) {
      if (data.status === 'not_found') {
        return displayMessage(gettext('Movie is not found in the database'));
      } else {
        return $('#movie' + movieId).fadeOut('fast', function() {
          return $(this).remove();
        });
      }
    }, function(){displayMessage(gettext('Error adding a movie'))}
    );
  };

  $scope.changeSearchType = function(id) {
    $scope.searchTypeId = id;
    if (id === 1) {
      $scope.searchType = gettext('Movie');
    }
    if (id === 2) {
      $scope.searchType = gettext('Actor');
    }
    if (id === 3) {
      $scope.searchType = gettext('Director');
    }
  };
}]);

$(function(){
  $('#search').show();
});
