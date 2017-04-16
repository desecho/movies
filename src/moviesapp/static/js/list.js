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
  function removeRecordFromPage(id) {
    function checkIfNoRecords() {
      if (!$('.movie').length) {
        $('#results').html(gettext('The list is empty') + '.');
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
      displayMessage(gettext('Error removing the movie'));
    });
  };

  $scope.switchMode = function(newMode) {
    function deactivateModeMinimal() {
      // TODO .comment, .comment-button fix display
      $('.poster, .comment, .release-date-label, .wall-post').show();
      $('.comment-button').hide();
      $('.details, .imdb-rating, .review, .release-date').css('display', '');
      $('.review').css('padding-top', '10px');
      $('.release-date, .imdb-rating').css({
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
      deactivateModeMinimal();
    }
    applySettings({
      mode: newMode
    }, false);
    $scope.mode = newMode;
  };

  $scope.saveComment = function(id) {
    const comment = $('#comment' + id).val();
    SaveComment.post($.param({
      id: id,
      comment: comment
    }), function(data) {
      if (!comment) {
        $scope.toggleCommentArea(id);
      }
    }, function() {
      displayMessage(gettext('Error saving a comment'));
    });
  };

  $scope.toggleCommentArea = function(id) {
    $('#comment-area' + id).toggle();
    $('#comment-area-button' + id).toggle();
    $('#comment' + id).focus();
  };
  $scope.mode = mode;
  $scope.isVkApp = isVkApp;
}]);

function changeRating(id, rating, element) {
  function revertToPreviousRating(element) {
    const scoreSettings = {
      score: element.attr('data-rating')
    };
    const settings = $.extend({}, ratySettings, ratyCustomSettings, scoreSettings);
    element.raty(settings);
  };

  $.post(urlChangeRating, {
    id: id,
    rating: rating
  }, function(data, error, x) {
    element.attr('data-rating', rating);
  }).fail(function() {
    revertToPreviousRating(element);
    displayMessage(gettext('Error adding a rating'));
  });
};

function switchSort(value) {
  let additionalSetting;
  if (value !== 'rating') {
    additionalSetting = {
      recommendation: false
    };
  } else {
    additionalSetting = {};
  }
  const settings = jQuery.extend({
    sort: value
  }, additionalSetting);
  applySettings(settings);
};

function applySettings(settings, reload) {
  if (reload == null) {
    reload = true;
  }
  $.post(urlApplySettings, {
    settings: JSON.stringify(settings)
  }, function(data) {
    if (reload) {
      location.reload();
    }
  }).fail(function() {
    displayMessage(gettext('Error applying the setting'));
  });
};

function activateModeMinimal() {
  $('.poster, .comment, .comment-button, .release-date-label, .wall-post').hide();
  $('.details, .review').css('display', 'inline');
  $('.review').css('padding-top', '0');
  $('.release-date, .imdb-rating').css({
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

function toggleRecommendation(){
  if (recommendation) {
    applySettings({
      recommendation: false
    });
  } else {
    applySettings({
      sort: 'rating',
      recommendation: true
    });
  }
};

function postToWall(id) {
  function post(photo) {
    function createWallPostMessage() {
      let text;
      const title = $('#record' + id).attr('data-title');
      const comment = $('#comment' + id).val();
      const ratingPost = ratySettings['hints'][rating - 1];
      if (rating > 2) {
        text = gettext('I recommend watching');
      } else {
        text = gettext("I don't recommend watching");
      }
      const myRating = gettext('My rating');
      text += ` "${title}".
${myRating} - ${ratingPost}.`
      if (comment) {
        text += '\n ' + comment;
      }
      return text;
    };

    function createWallPost() {
      const post = {message: createWallPostMessage()};
      if (photo) {
        post.attachments = photo;
      }
      return post;
    };

    return VK.api('wall.post', createWallPost(), function(data) {
      if (data.error) {
        const errorCode = data.error.error_code;
        if (errorCode !== 10007) {
          return displayMessage(gettext('Error posting to the wall #') + errorCode);
        }
      } else {
        return displayMessage(gettext('Your post has been posted'));
      }
    });
  };

  function saveWallPhoto(response) {
    return VK.api('photos.saveWallPhoto', response, function(data) {
      if (data.error) {
        return displayMessage(gettext('Error posting a poster to the wall #') + data.error.error_code);
      } else {
        return post(data.response[0].id);
      }
    });
  };

  function uploadPhotoToWall(url) {
    return $.post(urlAjaxUploadPhotoToWall, {
      url: url,
      recordId: id
    }, function(data) {
      return saveWallPhoto($.parseJSON(data.response));
    }).fail(function() {
      return displayMessage(gettext('Error loading a poster'));
    });
  };

  function getWallUploadServerAndUploadPhotoAndPostToWall() {
    return VK.api('photos.getWallUploadServer', function(data) {
      if (data.error) {
        return displayMessage(gettext('Error getting an upload server for wall posting #') + data.error.error_code);
      } else {
        return uploadPhotoToWall(data.response.upload_url);
      }
    });
  };

  function hasPoster() {
    return $('#record' + id).children('.poster').children('img').attr('src').indexOf('no_poster') === -1;
  };

  rating = parseInt($('#record' + id).children('.details').children('.review').children('.rating').attr('data-rating'));

  if (rating) {
    if (hasPoster()) {
      return getWallUploadServerAndUploadPhotoAndPostToWall();
    } else {
      return post();
    }
  } else {
    return displayMessage(gettext('Add a rating to the movie'));
  }
};

ratyCustomSettings = {
  readOnly: ratyReadonly,
  click: function(score) {
    if (!score) {
      score = 0;
    }
    changeRating($(this).attr('data-record-id'), score, $(this));
  }
};

$(function() {
  function setViewedIconsAndRemoveButtons() {
    if (anothersAccount) {
      $('.movie').each(function() {
        const id = $(this).attr('data-id');
        const listId = listData[id];
        setViewedIconAndRemoveButtons(id, listId);
      });
    }
  };

  if (mode === 'minimal') {
    activateModeMinimal();
  }

  if (recommendation) {
    $('#button-recommendation').button('toggle');
  }
  setViewedIconsAndRemoveButtons();
  autosize($('textarea'));
  retinajs();
  $('#results').show();
});
