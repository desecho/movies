var search_type = 1;
jQuery.validator.setDefaults({
    success: "valid"
});

function displayMovie(movie) {
  var html = '<div class="movie" id="movie' + movie.id + '"><div class="poster"><img src="' + movie.poster + '" alt="' + movie.title + ' poster"/></div>' +
         '<div class="title">' + movie.title + '</div>' + '<div class="details">';
  if (movie.release_date) {
    html += '<strong>Дата выпуска:</strong> ' + movie.release_date;
  }
  html += '</div><div class="buttons"><input type="button" class="btn" value="Просмотрено" onclick="add_to_list_from_tmdb(' + movie.id +
          ', 1)" /> <input class="btn" type="button" value="Хочу посмотреть" onclick="add_to_list_from_tmdb(' + movie.id + ', 2)" /></div></div>';
  $('#results').append(html);
}

function search_movie() {
  function isChecked(id) {
    if ($('#' + id).attr('checked')) {
      return 1;
    } else {
      return 0;
    }
  }

  $('#results').empty();
  var popular_only = isChecked('popular_only');
  var sort_by_date = isChecked('sort_by_date');
  var options = {'popular_only': popular_only, 'sort_by_date': sort_by_date};

  $.post(url_ajax_search_movie, {'query': $('#query').val(), 'type': search_type.toString(), 'options': options},
    function(data) {
      if (data.status == 1) {
        jQuery.each(data.movies, function(i, movie) {
          displayMovie(movie);
        });
      } else if (data.status === 0) {
        $('#results').html('Ничего не найдено.');
      } else {
        displayError('Ошибка поиска.');
      }
    }
  ).error(function() {
    displayError('Ошибка поиска.');
  });
}

function add_to_list_from_tmdb(movie_id, list_id) {
  $.post(url_ajax_add_to_list_from_tmdb,
        {'movie_id': movie_id, 'list_id': list_id },
        function(data) {
          if (data.status == -1) {
            displayError('Ошибка! Код #1.');
          }  else if (data.status == -2) {
            displayError('Ошибка! Код #2.');
          } else {
            $('#movie' + movie_id).fadeOut('fast', function() {
                $(this).remove();
            });
          }
        }).error(function() {displayError('Ошибка добавления фильма.');});
}

function change_search_type(id) {
    var text;
    var search_type;
    if (id == 1) {
        text = 'Фильм';
        search_type = 1;
    }
    if (id == 2) {
        text = 'Актёр';
        search_type = 2;
    }
    if (id == 3) {
        text = 'Режиссёр';
        search_type = 3;
    }
    $('#search_type_button').html(text + ' <span class="caret"></span>');
}

$(function() {
  $('#query').focus();
  $("#search").validate({
    rules: {
      query: "required"
    },
    messages: {
      query: "Введите запрос."
    },
    errorPlacement: function(error, element) {
      $('#error').html(error);
    },
    submitHandler: function(form) {
      search_movie();
    }
  });
});