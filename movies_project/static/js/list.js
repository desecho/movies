var raty_custom_settings = {
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
    settings = $.extend({}, raty_settings, raty_custom_settings, score_settings);
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
  apply_settings({'mode': value}, reload);
}

function switch_sort(value) {
  if (value != 'rating') {
    additional_setting = {'recommendation': false};
  } else {
    additional_setting = {};
  }
  settings = jQuery.extend({'sort': value}, additional_setting);
  apply_settings(settings);
}

function apply_settings(settings, reload) {
  reload = typeof reload !== 'undefined' ? reload : true;
  $.post(url_ajax_apply_settings, {'settings': JSON.stringify(settings)},
    function(data) {
      if(reload) {
        location.reload();
      }
    }
  ).error(function() {
    displayError('Ошибка применения настройки.');
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

function toggle_comment_area(id) {
  $('#comment_area' + id).toggle();
  $('#comment_area_button' + id).toggle();
  $('#comment' + id).focus();
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

function toggle_recommendation() {
  if (recommendation) {
    apply_settings({'recommendation': false});
  } else {
    apply_settings({'sort': 'rating', 'recommendation': true});
  }
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
  $('#button_mode_' + mode).button('toggle');
  if (mode == 'minimal') {
    activate_mode_minimal();
  }
  $('#button_sort_' + sort).button('toggle');
  if (recommendation) {
    $('#button_recommendation').button('toggle');
  }
  set_viewed_icons_and_remove_buttons();
});