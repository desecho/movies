app.factory('RemoveMovie', ['$resource', function($resource) {
  return $resource(urlRemoveMovie, {}, {
    post: {method: 'POST', headers: headers}
  });
}]);

app.factory('SaveComment', ['$resource', function($resource) {
  return $resource(urlSaveComment, {}, {
    post: {method: 'POST', headers: headers}
  });
}]);

app.controller('ListController', ['$scope', 'RemoveMovie', 'SaveComment',

function ($scope, RemoveMovie, SaveComment) {
  function removeMovieFromPage(id) {
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

  $scope.openUrl = function(url) {
    window.location.href = url;
  }

  $scope.removeMovie = function(id) {
    function error(){
      displayMessage(gettext('Error removing the movie'));
    }

    RemoveMovie.post($.param({id: id}), function(response) {
      if (response.status === 'success') {
        removeMovieFromPage(id);
      } else {
        error();
      }
    }, function(){
        error();
    });
  };

  $scope.switchMode = function(newMode) {
    function deactivateModeMinimal() {
      $('.poster, .comment, .release-date-label, .wall-post').show();
      $('.comment-button').hide();
      $('.details, .imdb-rating, .review, .release-date').css('display', '');
      $('.review').css('padding-top', '10px');
      $('.release-date, .imdb-rating').css({
        float: '',
        'margin-right': '0'
      });
      $('.movie').removeClass('movie-minimal');
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
  if (isVkUser) {
    $scope.isVkApp = isVkApp;
  }
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
    displayMessage(gettext('Error applying the settings'));
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
  $('.movie').addClass('movie-minimal');
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

  let ratyReadonly = anothersAccount || listId == 2
  window.ratyCustomSettings = {
    readOnly: ratyReadonly,
    click: function(score) {
      if (!score) {
        score = 0;
      }
      changeRating($(this).attr('data-record-id'), score, $(this));
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
