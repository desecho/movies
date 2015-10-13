App.factory('RemoveRecord', function($resource) {
  return $resource(urlRemoveRecord, {}, {
    post: {method: 'POST', headers: headers}
  });
});

App.controller('ListController', function ($scope, RemoveRecord) {
  $scope.remove_record = function(id) {
    RemoveRecord.post($.param({id: id}), function(data) {
      return remove_record_from_page(id);
    }, function(){
      display_message('Ошибка удаления фильма');
    });
  };
});

var activate_mode_minimal, apply_settings, change_rating, disactivate_mode_minimal, post_to_wall, raty_custom_settings, save_comment, switch_mode, switch_sort, toggle_comment_area, toggle_recommendation;

change_rating = function(id, rating, element) {
  var revert_to_previous_rating;
  revert_to_previous_rating = function(element) {
    var score_settings, settings;
    score_settings = {
      score: element.attr('data-rating')
    };
    settings = $.extend({}, raty_settings, raty_custom_settings, score_settings);
    return element.raty(settings);
  };
  return $.post(url_ajax_change_rating, {
    id: id,
    rating: rating
  }, function(data, error, x) {
    return element.attr('data-rating', rating);
  }).error(function() {
    revert_to_previous_rating(element);
    return display_message('Ошибка добавления оценки');
  });
};

switch_mode = function(value) {
  var reload;
  reload = false;
  if (value === 'minimal') {
    if (mode === 'full') {
      reload = true;
    } else {
      activate_mode_minimal();
      this.mode = 'minimal';
    }
  } else if (value === 'compact' && mode === 'minimal') {
    disactivate_mode_minimal();
    this.mode = 'compact';
  } else {
    reload = true;
  }
  return apply_settings({
    mode: value
  }, reload);
};

switch_sort = function(value) {
  var additional_setting, settings;
  if (value !== 'rating') {
    additional_setting = {
      recommendation: false
    };
  } else {
    additional_setting = {};
  }
  settings = jQuery.extend({
    sort: value
  }, additional_setting);
  return apply_settings(settings);
};

apply_settings = function(settings, reload) {
  if (reload == null) {
    reload = true;
  }
  return $.post(url_ajax_apply_settings, {
    settings: JSON.stringify(settings)
  }, function(data) {
    if (reload) {
      return location.reload();
    }
  }).error(function() {
    return display_message('Ошибка применения настройки');
  });
};

save_comment = function(id) {
  var comment;
  comment = $('#comment' + id).val();
  return $.post(url_ajax_save_comment, {
    id: id,
    comment: comment
  }, function(data) {
    if (!comment) {
      return toggle_comment_area(id);
    }
  }).error(function() {
    return display_message('Ошибка сохранения комментария');
  });
};

toggle_comment_area = function(id) {
  $('#comment_area' + id).toggle();
  $('#comment_area_button' + id).toggle();
  return $('#comment' + id).focus();
};

activate_mode_minimal = function() {
  $('.poster, .comment, .comment-button, .release_date_label, .rating_label, .wall-post').hide();
  $('.details, .review').css('display', 'inline');
  $('.review').css('padding-top', '0');
  $('.release_date, .imdb_rating').css({
    float: 'right',
    'margin-right': '10px'
  });
  return $('.movie').css({
    'width': '750px',
    'padding': '0',
    'border-width': '0 0 1px 0',
    'border-radius': '0',
    'margin': '10px 0 0 0',
    'min-height': '0'
  });
};

disactivate_mode_minimal = function() {
  $('.poster, .comment-button, .release_date_label, .rating_label, .wall-post').show();
  $('.details, .imdb_rating, .review, .release_date').css('display', '');
  $('.review').css('padding-top', '10px');
  $('.release_date, .imdb_rating').css({
    float: '',
    'margin-right': '0'
  });
  return $('.movie').css({
    'width': '730px',
    'border-width': '1px',
    'border-radius': '4px',
    'padding': '10px',
    'margin': '0 0 10px 0',
    'min-height': '145px'
  });
};

toggle_recommendation = function() {
  if (recommendation) {
    return apply_settings({
      recommendation: false
    });
  } else {
    return apply_settings({
      sort: 'rating',
      recommendation: true
    });
  }
};

$(function() {
  var set_viewed_icons_and_remove_buttons;
  set_viewed_icons_and_remove_buttons = function() {
    if (anothers_account) {
      return $('.movie').each(function() {
        var id, list_id;
        id = $(this).attr('data-id');
        list_id = list_data[id];
        return set_viewed_icon_and_remove_buttons(id, list_id);
      });
    }
  };
  $('#button_mode_' + mode).button('toggle');
  if (mode === 'minimal') {
    activate_mode_minimal();
  }
  $('#button_sort_' + sort).button('toggle');
  if (recommendation) {
    $('#button_recommendation').button('toggle');
  }
  return set_viewed_icons_and_remove_buttons();
});

post_to_wall = function(id) {
  var get_wall_upload_server_and_upload_photo_and_post_to_wall, has_poster, post, rating, save_wall_photo, upload_photo_to_wall;
  post = function(photo) {
    var create_wall_post, create_wall_post_message;
    create_wall_post_message = function() {
      var comment, rating_post, text, title;
      title = $('#record' + id).attr('data-title');
      comment = $('#comment' + id).val();
      rating_post = raty_settings['hints'][rating - 1];
      if (rating > 2) {
        text = 'Рекомендую посмотреть';
      } else {
        text = 'Не рекомендую смотреть';
      }
      text += " \"" + title + "\".\nМоя оценка - " + rating_post + ".";
      if (comment) {
        text += "\n " + comment;
      }
      return text;
    };
    create_wall_post = function() {
      post = {};
      post.message = create_wall_post_message();
      if (photo) {
        post.attachments = photo;
      }
      return post;
    };
    return VK.api('wall.post', create_wall_post(), function(data) {
      var error_code;
      if (data.error) {
        error_code = data.error.error_code;
        if (error_code !== 10007) {
          return display_message('Ошибка публикации на стену #' + error_code);
        }
      } else {
        return display_message('Запись отправлена на стену');
      }
    });
  };
  save_wall_photo = function(response) {
    return VK.api('photos.saveWallPhoto', response, function(data) {
      if (data.error) {
        return display_message('Ошибка сохранения изображения на стену #' + data.error.error_code);
      } else {
        return post(data.response[0].id);
      }
    });
  };
  upload_photo_to_wall = function(url) {
    return $.post(url_ajax_upload_photo_to_wall, {
      url: url,
      record_id: id
    }, function(data) {
      return save_wall_photo($.parseJSON(data.response));
    }).error(function() {
      return display_message('Ошибка загрузки изображения');
    });
  };
  get_wall_upload_server_and_upload_photo_and_post_to_wall = function() {
    return VK.api('photos.getWallUploadServer', function(data) {
      if (data.error) {
        return display_message('Ошибка получения сервера загрузки на стену #' + data.error.error_code);
      } else {
        return upload_photo_to_wall(data.response.upload_url);
      }
    });
  };
  rating = parseInt($('#record' + id).children('.details').children('.review').children('.rating').attr('data-rating'));
  has_poster = function() {
    return $('#record' + id).children('.poster').children('img').attr('src').indexOf('no_poster') === -1;
  };
  if (rating) {
    if (has_poster()) {
      return get_wall_upload_server_and_upload_photo_and_post_to_wall();
    } else {
      return post();
    }
  } else {
    return display_message('Поставьте оценку фильму');
  }
};

raty_custom_settings = {
  readOnly: raty_readonly,
  click: function(score) {
    if (!score) {
      score = 0;
    }
    return change_rating($(this).attr('data-record_id'), score, $(this));
  }
};

$(function() {
  return $('textarea').autosize();
});
