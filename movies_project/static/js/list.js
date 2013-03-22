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

function switch_mode(mode) {
  $.post(url_ajax_apply_setting, {'mode': mode},
    function(data) {
      location.reload();
    }
  ).error(function() {
    displayError('Ошибка смены режима.');
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
  set_viewed_icons_and_remove_buttons();
});