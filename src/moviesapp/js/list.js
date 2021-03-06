/* global VK:false */
/* global autosize:false */

'use strict';

import Vue from 'vue';
import axios from 'axios';
import {
  retina,
} from './helpers';
import {
  addToList,
  setViewedIconAndRemoveButtons,
} from './list_helpers';


function activateModeMinimal() {
  $('.poster, .comment, .comment-button, .release-date-label').hide();
  $('.details, .review').css('display', 'inline');
  $('.review').css('padding-top', '0');
  $('.release-date, .imdb-rating').css({
    'float': 'right',
    'margin-right': '10px',
  });
  $('.movie').addClass('movie-minimal');
}

function changeRating(id, rating, element) {
  function success() {
    element.data('rating', rating);
  }

  function fail() {
    function revertToPreviousRating(element) {
      const scoreSettings = {
        score: element.data('rating'),
      };
      const settings = $.extend({}, vars.ratySettings, ratyCustomSettings, scoreSettings);
      element.raty(settings);
    }

    revertToPreviousRating(element);
    Vue.prototype.$flashStorage.flash(gettext('Error adding a rating'), 'error', vars.flashOptions);
  }

  const url = urls.changeRating + id + '/';
  const data = $.param({
    rating: rating,
  });
  axios.put(url, data).then(success).catch(fail);
}

function applySettings(settings, reload = true) {
  const data = {
    settings: JSON.stringify(settings),
  };
  axios.put(urls.saveSettings, $.param(data)).then(function() {
    if (reload) {
      location.reload();
    }
  }).catch(function() {
    Vue.prototype.$flashStorage.flash(gettext('Error applying the settings'), 'error', vars.flashOptions);
  });
}

function setViewedIconsAndRemoveButtons() {
  if (vars.anothersAccount) {
    $('.movie').each(function() {
      const id = $(this).data('id'); // eslint-disable-line no-invalid-this
      const listId = vars.listData[id];
      setViewedIconAndRemoveButtons(id, listId);
    });
  }
}

window.vm = new Vue({
  el: '#app',
  data: {
    sortByDate: false,
    mode: vars.mode,
    isVkApp: vars.isVkApp,
    sort: vars.sort,
  },
  methods: {
    openUrl: function(url) {
      location.href = url;
    },
    saveOptions: function(recordId) {
      const options = {
        'original': $('#original_' + recordId).prop('checked'),
        'extended': $('#extended_' + recordId).prop('checked'),
        'theatre': $('#theatre_' + recordId).prop('checked'),
        'hd': $('#hd_' + recordId).prop('checked'),
        'fullHd': $('#full_hd_' + recordId).prop('checked'),
        '4k': $('#4k_' + recordId).prop('checked'),
        'words': $('#words_' + recordId).prop('checked'),
      };

      const data = $.param({
        options: JSON.stringify(options),
      });

      axios.put(urls.record + recordId + '/options/', data).then(function() {}).catch(function() {
        vm.flash(gettext('Error saving options'), 'error', vars.flashOptions);
      });
    },
    retinajs: retina,
    switchMode: function(newMode) {
      function deactivateModeMinimal() {
        $('.comment').each(function() {
          const el = $(this); // eslint-disable-line no-invalid-this
          const commentAreaToggle = $('#comment_area_button' + el.data('id'));
          const comment = el.find('textarea').val();
          if (comment) {
            el.show();
            commentAreaToggle.hide();
          } else {
            commentAreaToggle.show();
          }
        });
        $('.poster, .release-date-label').show();
        $('.details, .imdb-rating, .review, .release-date').css('display', '');
        $('.review').css('padding-top', '10px');
        $('.release-date, .imdb-rating').css({
          'float': '',
          'margin-right': '0',
        });
        $('.movie').removeClass('movie-minimal');
      }

      if (newMode == this.mode) {
        return;
      }
      if (newMode === 'minimal') {
        activateModeMinimal();
      } else {
        deactivateModeMinimal();
      }
      applySettings({
        mode: newMode,
      }, false);
      this.mode = newMode;
    },
    toggleRecommendation: function() {
      const newRecommendationSetting = !vars.recommendation;
      const settings = {
        recommendation: newRecommendationSetting,
      };
      if (newRecommendationSetting) {
        settings.sort = 'rating';
      }
      applySettings(settings);
    },
    switchSort: function(newSort) {
      if (this.sort == newSort) {
        return;
      }
      const settings = {
        sort: newSort,
      };
      if (newSort !== 'rating') {
        settings.recommendation = false;
      }
      applySettings(settings);
    },
    removeRecord: function(id) {
      function success() {
        function removeRecordFromPage(id) {
          $('#record' + id).fadeOut('fast', function() {
            $(this).remove(); // eslint-disable-line no-invalid-this
          });
        }
        removeRecordFromPage(id);
      }

      function fail() {
        vm.flash(gettext('Error removing the movie'), 'error', vars.flashOptions);
      }

      const url = urls.removeRecord + id + '/';
      axios.delete(url).then(success).catch(fail);
    },
    postToWall: function(id) {
      const vm = this;

      function post(photo) {
        function createWallPostMessage() {
          let text;
          const title = $('#record' + id).data('title');
          const comment = $('#comment' + id)[0].value;
          const ratingTexts = vars.ratySettings.hints;
          const ratingPost = ratingTexts[rating - 1];
          if (rating > 2) {
            text = gettext('I recommend watching');
          } else {
            text = gettext('I don\'t recommend watching');
          }
          const myRating = gettext('My rating');
          text += ` "${title}".\n${myRating} - ${ratingPost}.`;
          if (comment) {
            text += '\n' + comment;
          }
          return text;
        }

        function createWallPost() {
          const post = {
            message: createWallPostMessage(),
          };
          if (photo) {
            post.attachments = photo;
          }
          return post;
        }

        VK.api('wall.post', createWallPost(), function(response) {
          if (response.error) {
            // error_msg: "Operation denied by user"
            if (response.error.error_code === 10007) {
              return;
            }
            vm.flash(gettext('Error posting to the wall'), 'error', vars.flashOptions);
          } else {
            vm.flash(gettext('Your post has been posted'), 'success', vars.flashOptions);
          }
        });
      }

      function saveWallPhoto(data) {
        VK.api('photos.saveWallPhoto', data, function(response) {
          if (response.error) {
            vm.flash(gettext('Error posting a poster to the wall'), 'error', vars.flashOptions);
          } else {
            post(response.response[0].id);
          }
        });
      }

      function uploadPhotoToWall(uploadUrl) {
        const url = urls.uploadPosterToWall + id + '/';
        axios.post(url, $.param({
          url: uploadUrl,
        })).then(function(response) {
          const data = JSON.parse(response.data.data);
          saveWallPhoto(data);
        }).catch(function() {
          vm.flash(gettext('Error loading a poster'), 'error', vars.flashOptions);
        });
      }

      function getWallUploadServerAndUploadPhotoAndPostToWall() {
        VK.api('photos.getWallUploadServer', function(response) {
          if (response.error) {
            vm.flash(gettext('Error getting an upload server for wall posting'), 'error', vars.flashOptions);
          } else {
            uploadPhotoToWall(response.response.upload_url);
          }
        });
      }

      function hasPoster() {
        return ($('#record' + id).children('.poster').children('img').attr('src').indexOf('no_poster') ===
          -1);
      }

      const rating = $('#record' + id).children('.details').children('.review').children('.rating').data('rating');

      if (rating) {
        if (hasPoster()) {
          getWallUploadServerAndUploadPhotoAndPostToWall();
        } else {
          post();
        }
      } else {
        vm.flash(gettext('Add a rating to the movie'), 'info', vars.flashOptions);
      }
    },
    addToList: addToList,
    toggleCommentArea: function(id) {
      $('#comment-area' + id).toggle();
      $('#comment-area-button' + id).toggle();
      $('#comment' + id).focus();
    },
    saveComment: function(id) {
      const comment = $('#comment' + id)[0].value;
      const data = $.param({
        id: id,
        comment: comment,
      });
      axios.put(urls.saveComment, data).then(function() {
        const commentAreaToggle = $('#comment_area_button' + id);
        if (comment) {
          commentAreaToggle.hide();
        }
        if (!comment) {
          vm.toggleCommentArea(id);
          commentAreaToggle.show();
        }
      }).catch(function() {
        vm.flash(gettext('Error saving a comment'), 'error', vars.flashOptions);
      });
    },
  },
});

const ratyCustomSettings = {
  readOnly: vars.anothersAccount || vars.listId == 2,
  click: function(score) {
    if (!score) {
      score = 0;
    }
    changeRating($(this).data('record-id'), score, $(this));
  },
};

if (vars.mode === 'minimal') {
  activateModeMinimal();
}

(function() {
  const settings = $.extend({}, vars.ratySettings, ratyCustomSettings);
  $('.rating').raty(settings);
})();

if (vars.recommendation) {
  $('#button-recommendation').button('toggle');
}

setViewedIconsAndRemoveButtons();
autosize($('textarea'));
