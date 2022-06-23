/* global VK:false */

'use strict';

import axios from 'axios';
import {retina, removeItemOnce} from './helpers';
import {newApp} from './app';
import autosize from 'autosize';

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


window.vm = newApp({
  data() {
    return {
      sortByDate: false,
      records: vars.records,
      mode: vars.mode,
      isVkApp: vars.isVkApp,
      sort: vars.sort,
      listWatchedId: vars.listWatchedId,
      listToWatchId: vars.listToWatchId,
      listId: vars.listId,
      isAnothersAccount: vars.isAnothersAccount,
      recommendations: vars.recommendations,
    };
  },
  methods: {
    openUrl(url) {
      location.href = url;
    },
    getSrcSet(img1x, img2x) {
      return `${img1x} 1x, ${img2x} 2x`;
    },
    retinajs: retina,
    saveOptions(record) {
      const data = {
        options: record.options,
      };
      const vm = this;

      axios.put(urls.record + record.id + '/options/', data).then(function() {}).catch(function() {
        vm.$toast.error(gettext('Error saving options'));
      });
    },
    switchMode(newMode) {
      if (newMode == this.mode) {
        return;
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
      const vm = this;
      if (vm.sort == newSort) {
        return;
      }
      vm.sort = newSort;
      const settings = {
        sort: newSort,
      };
      if (newSort !== 'rating') {
        // disable recommendation if sorting by rating is manually disabled
        settings.recommendation = false;
      }
      applySettings(settings);
    },
    removeRecord(record) {
      function success() {
        removeItemOnce(vm.records, record);
      }

      function fail() {
        vm.$toast.error(gettext('Error removing the movie'));
      }
      const vm = this;
      const url = urls.removeRecord + record.id + '/';
      axios.delete(url).then(success).catch(fail);
    },
    postToWall(record) {
      function post(photoId, ownerId) {
        function createWallPostMessage() {
          let text;
          const title = movie.title;
          const comment = record.comment;
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
        const url = urls.uploadPosterToWall + record.id + '/';
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
      const vm = this;
      const rating = record.rating;
      const movie = record.movie;

      if (rating) {
        if (record.movie.hasPoster) {
          getWallUploadServerAndUploadPhotoAndPostToWall();
        } else {
          post(null, null);
        }
      } else {
        vm.$toast.info(gettext('Add a rating to the movie'));
      }
    },
    addToList(movieId, listId, record) {
      const url = urls.addToList + movieId + '/';
      const vm = this;
      axios.post(url, {
        listId: listId,
      }).then(function() {
        record.listId = listId;
      }).catch(function() {
        vm.$toast.error(gettext('Error adding the movie to the list'));
      });
    },
    showCommentArea(record) {
      record.commentArea = true;
    },
    saveComment(record) {
      const vm = this;
      const data = {
        comment: record.comment,
      };
      axios.put(urls.saveComment + record.id + '/', data).then(function() {
        if (record.comment == '') {
          record.commentArea = false;
        }
      }).catch(function() {
        vm.$toast.error(gettext('Error saving a comment'));
      });
    },
  },
});

window.vm.mount('#app');

const ratyCustomSettings = {
  readOnly: vars.isAnothersAccount || vars.listId == vars.listToWatchId,
  click: function(score) {
    if (!score) {
      score = 0;
    }
    changeRating($(this).data('record-id'), score, $(this));
  },
};

(function() {
  const settings = $.extend({}, vars.ratySettings, ratyCustomSettings);
  $('.rating').raty(settings);
})();

autosize($('textarea'));
