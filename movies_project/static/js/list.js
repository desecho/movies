app.factory('RemoveRecord', ['$resource', function($resource) {
  return $resource(urlRemoveRecord, {}, {
    post: {method: 'POST', headers: headers}
  });
}]);

app.factory('SaveComment', ['$resource', function($resource) {
  return $resource(urlSaveComment, {}, {
    post: {method: 'POST', headers: headers}
  });
}]);

app.controller('ListController', ['$scope', 'RemoveRecord', 'SaveComment',

function ($scope, RemoveRecord, SaveComment) {
    removeRecordFromPage = function(id) {
      function checkIfNoRecords() {
        if (!$('.movie').length) {
          $('#results').html('Список пуст.');
        }
      };
      $('#record' + id).fadeOut('fast', function() {
        $(this).remove();
        checkIfNoRecords();
      });
    };
  $scope.removeRecord = function(id) {
    RemoveRecord.post($.param({id: id}), function(data) {
      removeRecordFromPage(id);
    }, function(){
      displayMessage('Ошибка удаления фильма');
    });
  };
  $scope.mode = mode;
  $scope.switchMode = function(newMode) {
    function disactivateModeMinimal() {
      // TODO .comment, .comment-button fix display
      $('.poster, .comment, .release_date_label, .rating_label, .wall-post').show();
      $('.comment-button').hide();
      $('.details, .imdb_rating, .review, .release_date').css('display', '');
      $('.review').css('padding-top', '10px');
      $('.release_date, .imdb_rating').css({
        float: '',
        'margin-right': '0'
      });
      $('.movie').css({
        'width': '730px',
        'border-width': '1px',
        'border-radius': '4px',
        'padding': '10px',
        'margin': '0 0 10px 0',
        'min-height': '145px'
      });
    };
    if (newMode === 'minimal') {
      activateModeMinimal();
    } else {
      disactivateModeMinimal();
    }
    apply_settings({
      mode: newMode
    }, false);
    $scope.mode = newMode;
  };
  $scope.saveComment = function(id) {
    var comment = $('#comment' + id).val();
    SaveComment.post($.param({
      id: id,
      comment: comment
    }), function(data) {
      if (!comment) {
        $scope.toggleCommentArea(id);
      }
    }, function() {
      displayMessage('Ошибка сохранения комментария');
    });
  };

  $scope.toggleCommentArea = function(id) {
    $('#comment_area' + id).toggle();
    $('#comment_area_button' + id).toggle();
    $('#comment' + id).focus();
  };
}]);

var activateModeMinimal, apply_settings, post_to_wall, ratyCustomSettings, switch_sort, toggle_recommendation;

function changeRating(id, rating, element) {
  function revertToPreviousRating(element) {
    var scoreSettings = {
      score: element.attr('data-rating')
    };
    var settings = $.extend({}, ratySettings, ratyCustomSettings, scoreSettings);
    element.raty(settings);
  };
  $.post(urlChangeRating, {
    id: id,
    rating: rating
  }, function(data, error, x) {
    element.attr('data-rating', rating);
  }).error(function() {
    revertToPreviousRating(element);
    displayMessage('Ошибка добавления оценки');
  });
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
  apply_settings(settings);
};

apply_settings = function(settings, reload) {
  if (reload == null) {
    reload = true;
  }
  $.post(url_ajax_apply_settings, {
    settings: JSON.stringify(settings)
  }, function(data) {
    if (reload) {
      location.reload();
    }
  }).error(function() {
    displayMessage('Ошибка применения настройки');
  });
};

activateModeMinimal = function() {
  $('.poster, .comment, .comment-button, .release_date_label, .rating_label, .wall-post').hide();
  $('.details, .review').css('display', 'inline');
  $('.review').css('padding-top', '0');
  $('.release_date, .imdb_rating').css({
    float: 'right',
    'margin-right': '10px'
  });
  $('.movie').css({
    'width': '750px',
    'padding': '0',
    'border-width': '0 0 1px 0',
    'border-radius': '0',
    'margin': '10px 0 0 0',
    'min-height': '0'
  });
};

toggle_recommendation = function() {
  if (recommendation) {
    apply_settings({
      recommendation: false
    });
  } else {
    apply_settings({
      sort: 'rating',
      recommendation: true
    });
  }
};

$(function() {
  var set_viewed_icons_and_remove_buttons;
  set_viewed_icons_and_remove_buttons = function() {
    if (anothers_account) {
      $('.movie').each(function() {
        var id, list_id;
        id = $(this).attr('data-id');
        list_id = list_data[id];
        set_viewed_icon_and_remove_buttons(id, list_id);
      });
    }
  };
  $('#button_mode_' + mode).button('toggle');
  if (mode === 'minimal') {
    activateModeMinimal();
  }
  $('#button_sort_' + sort).button('toggle');
  if (recommendation) {
    $('#button_recommendation').button('toggle');
  }
  set_viewed_icons_and_remove_buttons();
});

post_to_wall = function(id) {
  var get_wall_upload_server_and_upload_photo_and_post_to_wall, has_poster, post, rating, save_wall_photo, upload_photo_to_wall;
  post = function(photo) {
    var create_wall_post, create_wall_post_message;
    create_wall_post_message = function() {
      var comment, rating_post, text, title;
      title = $('#record' + id).attr('data-title');
      comment = $('#comment' + id).val();
      rating_post = ratySettings['hints'][rating - 1];
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
          return displayMessage('Ошибка публикации на стену #' + error_code);
        }
      } else {
        return displayMessage('Запись отправлена на стену');
      }
    });
  };
  save_wall_photo = function(response) {
    return VK.api('photos.saveWallPhoto', response, function(data) {
      if (data.error) {
        return displayMessage('Ошибка сохранения изображения на стену #' + data.error.error_code);
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
      return displayMessage('Ошибка загрузки изображения');
    });
  };
  get_wall_upload_server_and_upload_photo_and_post_to_wall = function() {
    return VK.api('photos.getWallUploadServer', function(data) {
      if (data.error) {
        return displayMessage('Ошибка получения сервера загрузки на стену #' + data.error.error_code);
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
    return displayMessage('Поставьте оценку фильму');
  }
};

ratyCustomSettings = {
  readOnly: raty_readonly,
  click: function(score) {
    if (!score) {
      score = 0;
    }
    changeRating($(this).attr('data-record_id'), score, $(this));
  }
};

$(function() {
  $('textarea').autosize();
});
