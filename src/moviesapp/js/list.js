/* global VK:false */

'use strict';

import axios from 'axios';
import {retina} from './helpers';
import {newApp} from './app';
import {
  addToList,
  setViewedIconAndRemoveButtons,
} from './list_helpers';
import autosize from 'autosize';

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
    vm.$toast.error(gettext('Error adding a rating'));
  }

  const url = urls.changeRating + id + '/';
  axios.put(url, {rating: rating}).then(success).catch(fail);
}

function applySettings(settings, reload = true) {
  const data = {
    settings: settings,
  };
  axios.put(urls.saveSettings, data).then(function() {
    if (reload) {
      location.reload();
    }
  }).catch(function() {
    vm.$toast.error(gettext('Error applying the settings'));
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


window.vm = newApp({
  data() {
    return {
      sortByDate: false,
      mode: vars.mode,
      isVkApp: vars.isVkApp,
      sort: vars.sort,
      listWatchedId: vars.listWatchedId,
      listToWatchId: vars.listToWatchId,
    };
  },
  methods: {
    openUrl(url) {
      location.href = url;
    },
    retinajs: retina,
    saveOptions(recordId) {
      const options = {
        'original': $('#original_' + recordId).prop('checked'),
        'extended': $('#extended_' + recordId).prop('checked'),
        'theatre': $('#theatre_' + recordId).prop('checked'),
        'hd': $('#hd_' + recordId).prop('checked'),
        'fullHd': $('#full_hd_' + recordId).prop('checked'),
        '4k': $('#4k_' + recordId).prop('checked'),
      };

      const data = {
        options: options,
      };
      const vm = this;

      axios.put(urls.record + recordId + '/options/', data).then(function() {}).catch(function() {
        vm.$toast.error(gettext('Error saving options'));
      });
    },
    switchMode(newMode) {
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
    toggleRecommendation() {
      const newRecommendationSetting = !vars.recommendation;
      const settings = {
        recommendation: newRecommendationSetting,
      };
      if (newRecommendationSetting) {
        settings.sort = 'rating';
      }
      applySettings(settings);
    },
    switchSort(newSort) {
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
    removeRecord(id) {
      function success() {
        function removeRecordFromPage(id) {
          $('#record' + id).fadeOut('fast', function() {
            $(this).remove(); // eslint-disable-line no-invalid-this
          });
        }
        removeRecordFromPage(id);
      }

      function fail() {
        vm.$toast.error(gettext('Error removing the movie'));
      }
      const vm = this;
      const url = urls.removeRecord + id + '/';
      axios.delete(url).then(success).catch(fail);
    },
    postToWall(id) {
      function post(photoId, ownerId) {
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
          if (photoId) {
            post.attachments = `photo${ownerId}_${photoId}`;
          }
          return post;
        }

        VK.api('wall.post', createWallPost(), function(response) {
          if (response.error) {
            // error_msg: "Operation denied by user"
            if (response.error.error_code === 10007) {
              return;
            }
            vm.$toast.error(gettext('Error posting to the wall'));
          } else {
            vm.$toast.success(gettext('Your post has been posted'));
          }
        });
      }

      function saveWallPhoto(data) {
        VK.api('photos.saveWallPhoto', data, function(response) {
          if (response.error) {
            vm.$toast.error(gettext('Error posting a poster to the wall'));
          } else {
            const responseData = response.response[0];
            post(responseData.id, responseData.owner_id);
          }
        });
      }

      function uploadPhotoToWall(uploadUrl) {
        const url = urls.uploadPosterToWall + id + '/';
        axios.post(url, {
          url: uploadUrl,
        }).then(function(response) {
          const data = JSON.parse(response.data.data);
          saveWallPhoto(data);
        }).catch(function() {
          vm.$toast.error(gettext('Error loading a poster'));
        });
      }

      function getWallUploadServerAndUploadPhotoAndPostToWall() {
        VK.api('photos.getWallUploadServer', function(response) {
          if (response.error) {
            vm.$toast.error(gettext('Error getting an upload server for wall posting'));
          } else {
            uploadPhotoToWall(response.response.upload_url);
          }
        });
      }

      function hasPoster() {
        return ($('#record' + id).children('.poster').children('img').attr('src').indexOf('no_poster') ===
          -1);
      }
      const vm = this;
      const rating = $('#record' + id).children('.details').children('.review').children('.rating').data('rating');

      if (rating) {
        if (hasPoster()) {
          getWallUploadServerAndUploadPhotoAndPostToWall();
        } else {
          post(null, null);
        }
      } else {
        vm.$toast.info(gettext('Add a rating to the movie'));
      }
    },
    addToList: addToList,
    toggleCommentArea(id) {
      $('#comment-area' + id).toggle();
      $('#comment-area-button' + id).toggle();
      $('#comment' + id).focus();
    },
    saveComment(id) {
      const vm = this;
      const comment = $('#comment' + id)[0].value;
      const data = {
        comment: comment,
      };
      axios.put(urls.saveComment + id + '/', data).then(function() {
        const commentAreaToggle = $('#comment_area_button' + id);
        if (comment) {
          commentAreaToggle.hide();
        }
        if (!comment) {
          vm.toggleCommentArea(id);
          commentAreaToggle.show();
        }
      }).catch(function() {
        vm.$toast.error(gettext('Error saving a comment'));
      });
    },
  },
});

window.vm.mount('#app');

const ratyCustomSettings = {
  readOnly: vars.anothersAccount || vars.listId == vars.listToWatchId,
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
