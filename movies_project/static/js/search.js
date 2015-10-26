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
  $scope.searchType = 'Фильм';
  $scope.searchTypeId = 1;
  $scope.submit = function(){
    $scope.searchResults = [];
    var options = {
      popular_only: $('#popular_only').prop('checked'),
      sort_by_date: $('#sort_by_date').prop('checked')
    };
    SearchMovie.get({
      query: $scope.query,
      type: $scope.searchTypeId.toString(),
      options: $.param(options)
    }, function(data) {
      $scope.nothing_found = false;
      if (data.status === 1) {
        $scope.searchResults = data.movies;
      } else if (data.status === 0) {
        $scope.nothing_found = true;
      } else {
        displayMessage('Ошибка поиска');
      }
    }, function(){displayMessage('Ошибка поиска')}
    );
  }

  $scope.addToListFromDb = function(movie_id, list_id) {
    AddToListFromDb.post($.param({
      movie_id: movie_id,
      list_id: list_id
    }), function(data) {
      if (data.status === -1) {
        return displayMessage('Ошибка! Код #1');
      } else if (data.status === -2) {
        return displayMessage('Ошибка! Код #2');
      } else {
        return $('#movie' + movie_id).fadeOut('fast', function() {
          return $(this).remove();
        });
      }
    }, function(){displayMessage('Ошибка добавления фильма')}
    );
  };

  $scope.changeSearchType = function(id) {
    $scope.searchTypeId = id;
    if (id === 1) {
      $scope.searchType = 'Фильм';
    }
    if (id === 2) {
      $scope.searchType = 'Актёр';
    }
    if (id === 3) {
      $scope.searchType = 'Режиссёр';
    }
  };
}]);