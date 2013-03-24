var general_settings = {
  hints: ['ужасно','плохо','нормально','хорошо','великолепно'],
  noRatedMsg:'Пока нет оценки',
  path: '/static/libs/raty/',
  cancel: true,
  readOnly : anothers_account,
  click: function(score) {
    //change from null to 0 to simplify saving
    if (!score) {
      score = 0;
    }
    change_rating($(this).attr('data-record_id'), score, $(this));
  }
};

function change_rating(id, rating, element) {
  function revert_to_previous_rating(element) {
    score_settings = {score: element.attr('data-rating')};
    settings = $.extend({}, general_settings, score_settings);
    element.raty(settings);
  }

  $.post(url_ajax_change_rating, {'id': id, 'rating': rating},
    function(data, error, x) {
      //update current rating
      element.attr('data-rating', rating);
    }
  ).error(function() {
    revert_to_previous_rating(element);
    displayError('Ошибка добавления оценки.');
  });
}

function remove_record_from_page(id) {
  $('#record' + id).fadeOut('fast', function() {
    $(this).remove();
    check_if_no_records();
  });
}

function remove_record(id) {
  $.post(url_ajax_remove_record, {'id': id},
    function(data) {
      remove_record_from_page(id);
    }
  ).error(function() {
    displayError('Ошибка удаления фильма.');
  });
}

function switch_mode(value) {
  var reload = false;
  if (value == 'minimal') {
    if (mode == 'full') {
      reload = true;
    } else {
      activate_mode_minimal();
      mode = 'minimal';
    }
  } else if (value == 'compact' && mode == 'minimal') {
    disactivate_mode_minimal();
    mode = 'compact';
  } else {
    reload = true;
  }
  apply_setting('mode', value, reload);
}

function switch_sort(value) {
  apply_setting('sort', value);
}

function apply_setting(type, value, reload) {
  reload = typeof reload !== 'undefined' ? reload : true;
  $.post(url_ajax_apply_setting, {'type': type, 'value': value},
    function(data) {
      if(reload) {
        location.reload();
      }
    }
  ).error(function() {
    displayError('Ошибка применения настройки.');
  });
}

function add_to_list(movie_id, list_id, record_id) {
  $.post(url_ajax_add_to_list, {'movie_id': movie_id, 'list_id': list_id},
        function(data) {
          if (!anothers_account) {
            remove_record_from_page(record_id);
          } else {
            set_viewed_icon_and_remove_buttons(record_id, list_id);
          }
        }
  ).error(function() {
      displayError('Ошибка добавления фильма в список.');
  });
}

function save_comment(id) {
  comment = $('#comment' + id).val();
  $.post(url_ajax_save_comment, {'id': id, 'comment': comment},
    function(data) {
      if (!comment) {
        toggle_comment_area(id);
      }
    }
  ).error(function() {
    displayError('Ошибка сохранения комментария.');
  });
}

function check_if_no_records() {
  if (!$('.movie').length) {
    $('#results').html('Список пуст.');
  }
}

function toggle_comment_area(id) {
  $('#comment_area' + id).toggle();
  $('#comment_area_button' + id).toggle();
  $('#comment' + id).focus();
}

function set_viewed_icon_and_remove_buttons(record_id, list_id) {
  function remove_buttons(){
    $('#record' + record_id).children('.buttons').html('');
  }
  set_viewed_icon(record_id, list_id);
  if (list_id !== 0) {
    remove_buttons();
  }
}

function set_viewed_icon(record_id, list_id) {
  var icon;
  if (list_id === 0) {
    return;
  }
  if (list_id == 1) {
    icon = 'open';
  }
  if (list_id == 2) {
    icon = 'close';
  }
  var html = '<i class="icon-eye-' + icon + '"></i>';
  $('#record' + record_id).children('.title').prepend(html);
}

function activate_mode_minimal() {
  $('.poster, .comment, .release_date_label, .rating_label').hide();
  $('.details, .review').css('display', 'inline');
  $('.review').css('padding-top', '0');
  $('.release_date, .imdb_rating').css({'float': 'right', 'margin-right': '10px'});
  $('.movie').css({'padding-top': '0', 'margin-top': '7px', 'min-height': 'auto'});
}

function disactivate_mode_minimal() {
  $('.poster, .comment, .release_date_label, .rating_label').show();
  $('.details, .imdb_rating, .review, .release_date').css('display', '');
  $('.review').css('padding-top', '10px');
  $('.release_date, .imdb_rating').css({'float': '', 'margin-right': '0'});
  $('.movie').css({'padding-top': '20px', 'margin-top': '0', 'min-height': '145px'});
}

function get_torrents(query) {
  function bytes_to_size(bytes, precision) {
    var kilobyte = 1024;
    var megabyte = kilobyte * 1024;
    var gigabyte = megabyte * 1024;
    var terabyte = gigabyte * 1024;
    if ((bytes >= 0) && (bytes < kilobyte)) {
      return bytes + ' B';
    } else if ((bytes >= kilobyte) && (bytes < megabyte)) {
      return (bytes / kilobyte).toFixed(precision) + ' KB';
    } else if ((bytes >= megabyte) && (bytes < gigabyte)) {
      return (bytes / megabyte).toFixed(precision) + ' MB';
    } else if ((bytes >= gigabyte) && (bytes < terabyte)) {
      return (bytes / gigabyte).toFixed(precision) + ' GB';
    } else if (bytes >= terabyte) {
      return (bytes / terabyte).toFixed(precision) + ' TB';
    } else {
      return bytes + ' B';
    }
  }
  $.ajax({
    type: "POST",
    url: url_ajax_download,
    data: {'query': query},
    success: function(json) {
        json = $.parseJSON(json.data);
        var total_lists = json.items.list.length;
        if (total_lists === 0) {
            $("#torrents").html('Торрентов не найдено.');
        } else {
          html = '<ul>';
          for (var i = 1; i < total_lists; i++) {
            html += '<li id="searchresult-' + i + '"><a href="' + json.items.list[i].uri + '" target="_blank">' + json.items.list[i].title + '</a> &#8593; ' + json.items.list[i].Seeds + ' &#8595; ' + json.items.list[i].leechers + '<br>' + json.items.list[i].tracker + ' &mdash; ' + bytes_to_size(json.items.list[i].size, 2) + ' &mdash; ' + json.items.list[i].regtime + '</li>'
          }
          html += '</ul>';
          $("#torrents").html(html);
        }
      },
    async: false
  }).error(function() {
    displayError('Ошибка поиска торрентов.');
  });
}

function show_torrents(query) {
  get_torrents(query);
  $('#myModal').modal('toggle');
}

$(function() {
  function set_viewed_icons_and_remove_buttons(){
    if (anothers_account) {
      $('.movie').each(function(){
          var id = $(this).attr('data-id');
          var list_id = list_data[id];
          set_viewed_icon_and_remove_buttons(id, list_id);
        }
      );
    }
  }
  score_settings = {
    score: function() {
      return $(this).attr('data-rating');
    }
  };
  settings = $.extend({}, general_settings, score_settings);
  $('.rating').raty(settings);
  $('#button_mode_' + mode).button('toggle');
  if (mode == 'minimal') {
    activate_mode_minimal();
  }
  $('#button_sort_' + sort).button('toggle');
  set_viewed_icons_and_remove_buttons();
});