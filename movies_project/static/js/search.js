App.factory('SearchMovie', function($resource) {
  return $resource(urlSearchMovie, {}, {
    get: {method: 'GET'}
  });
});

App.factory('AddToListFromDb', function($resource) {
  return $resource(urlAddToListFromDb, {}, {
    post: {method: 'POST', headers: headers}
  });
});

App.controller('MoviesSearchController', function ($scope, SearchMovie, AddToListFromDb) {
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
        display_message('Ошибка поиска');
      }
    }, function(){display_message('Ошибка поиска')}
    );
  }

  $scope.addToListFromDb = function(movie_id, list_id) {
    AddToListFromDb.post($.param({
      movie_id: movie_id,
      list_id: list_id
    }), function(data) {
      if (data.status === -1) {
        return display_message('Ошибка! Код #1');
      } else if (data.status === -2) {
        return display_message('Ошибка! Код #2');
      } else {
        return $('#movie' + movie_id).fadeOut('fast', function() {
          return $(this).remove();
        });
      }
    }, function(){display_message('Ошибка добавления фильма')}
    );
  };

  $scope.changeSearchType = function(id) {
    if (id === 1) {
      $scope.searchType = 'Фильм';
      $scope.searchTypeId = 1;
    }
    if (id === 2) {
      $scope.searchType = 'Актёр';
      $scope.searchTypeId = 2;
    }
    if (id === 3) {
      $scope.searchType = 'Режиссёр';
      $scope.searchTypeId = 3;
    }
  };
});