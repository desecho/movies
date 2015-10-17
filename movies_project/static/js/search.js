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

App.directive('dynamic', function ($compile) {
  return {
    restrict: 'A',
    replace: true,
    link: function (scope, ele, attrs) {
      scope.$watch(attrs.dynamic, function(html) {
        ele.html(html);
        $compile(ele.contents())(scope);
      });
    }
  };
});

App.controller('MoviesSearchController', function ($scope, SearchMovie, AddToListFromDb) {
  $scope.searchType = 'Фильм';
  $scope.searchTypeId = 1;
  $scope.submit = function(){
    $scope.searchResults = '';
    var options = {
      popular_only: $('#popular_only').prop('checked'),
      sort_by_date: $('#sort_by_date').prop('checked')
    };
    SearchMovie.get({
      query: $scope.query,
      type: $scope.searchTypeId.toString(),
      options: $.param(options)
    }, function(data) {
      function displayMovie(movie) {
        var html;
        html = "<div class=\"movie\" id=\"movie" + movie.id + "\">\n<div class=\"poster\"><img src=\"" + movie.poster + "\" alt=\"" + movie.title + " poster\"/></div>\n<div class=\"title\">" + movie.title + "\n  <div class=\"add-to-list-buttons\">\n    <a href=\"#\" title=\"Добавить в список Просмотрено\" ng-click=\"addToListFromDb(" + movie.id + ", 1)\"><i class=\"fa fa-eye\"></i></a>\n    <a href=\"#\" title=\"Добавить в список К просмотру\" ng-click=\"addToListFromDb(" + movie.id + ", 2)\"><i class=\"fa fa-eye-slash\"></i></a>\n  </div>\n</div>\n<div class=\"details\">";
        if (movie.release_date) {
          html += "<strong>Дата выпуска:</strong> " + movie.release_date;
        }
        html += '</div></div>';
        return html;
      };

      if (data.status === 1) {
        var html = ''
        jQuery.each(data.movies, function(i, movie) {
          html += displayMovie(movie);
        });
        $scope.searchResults = html;
      } else if (data.status === 0) {
        $scope.searchResults ='Ничего не найдено';
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