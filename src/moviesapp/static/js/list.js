/* global autosize:false */
/* global VK:false */

'use strict';

(function() {
  angular.module('app').factory('recordService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlRemoveRecord + ':id/', {
      id: '@id',
    }, {
      delete: {
        method: 'DELETE',
      },
    });
  }
})();

(function() {
  angular.module('app').factory('recordDataservice', factory);
  factory.$inject = ['recordService', 'growl'];

  function factory(recordService, growl) {
    return {
      delete: deleteMovie,
    };

    function deleteMovie(id) {
      return recordService.delete({
        id: id,
      }, success, fail);

      function removeRecordFromPage(id) {
        function checkIfNoRecords() {
          if (!angular.element('.movie').length) {
            angular.element('#results')[0].innerHTML = gettext('The list is empty') + '.';
          }
        }
        angular.element('#record' + id).fadeOut('fast', function(el) {
          angular.element(this).remove(); // eslint-disable-line no-invalid-this
          checkIfNoRecords();
        });
      }

      function success() {
        removeRecordFromPage(id);
      }

      function fail() {
        growl.error(gettext('Error removing the movie'));
      }
    }
  }
})();

(function() {
  angular.module('app').factory('movieCommentService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlSaveComment, {}, {
      save: {
        method: 'PUT',
      },
    });
  }
})();

(function() {
  angular.module('app').factory('movieCommentDataservice', factory);
  factory.$inject = ['movieCommentService', 'growl'];

  function factory(movieCommentService, growl) {
    return {
      save: save,
    };

    function save(data) {
      return movieCommentService.save(angular.element.param(data), success, fail);

      function success(response) {
        if (response.status !== 'success') {
          fail();
        }
      }

      function fail() {
        growl.error(gettext('Error saving a comment'));
      }
    }
  }
})();


(function() {
  angular.module('app').factory('ratingService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlChangeRating + ':id/', {
      id: '@id',
    }, {
      save: {
        method: 'PUT',
      },
    });
  }
})();


(function() {
  angular.module('app').factory('ratingDataservice', factory);
  factory.$inject = ['ratingService', 'growl', 'ratySettings'];

  function factory(ratingService, growl, ratySettings) {
    return {
      save: save,
    };

    function save(id, rating, element, ratyCustomSettings) {
      return ratingService.save({
        id: id,
      }, angular.element.param({
        rating: rating,
      }), success, fail);

      function success(response) {
        element.data('rating', rating);
      }

      function fail() {
        function revertToPreviousRating(element) {
          const scoreSettings = {
            score: element.data('rating'),
          };
          const settings = angular.extend({}, ratySettings, ratyCustomSettings, scoreSettings);
          element.raty(settings);
        }

        revertToPreviousRating(element);
        growl.error(gettext('Error adding a rating'));
      }
    }
  }
})();

(function() {
  angular.module('app').factory('settingsService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlSaveSettings, {}, {
      save: {
        method: 'PUT',
      },
    });
  }
})();

(function() {
  angular.module('app').factory('settingsDataservice', factory);
  factory.$inject = ['settingsService', 'growl'];

  function factory(settingsService, growl) {
    return {
      save: save,
    };

    function save(settings) {
      return settingsService.save(angular.element.param({
        settings: angular.toJson(settings),
      }), function() {}, fail);

      function fail() {
        growl.error(gettext('Error applying the settings'));
      }
    }
  }
})();

(function() {
  angular.module('app').factory('photoService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlUploadPosterToWall + ':id/', {
      id: '@id'
    }, {
      upload: {
        method: 'POST',
      },
    });
  }
})();

(function() {
  angular.module('app').factory('photoDataservice', factory);
  factory.$inject = ['photoService', 'growl'];

  function factory(photoService, growl) {
    return {
      upload: upload,
    };

    function upload(id, url) {
      return photoService.upload({
        id: id
      }, angular.element.param({
        url: url,
      }), success, fail);

      function success(response) {
        response.data = angular.fromJson(response.data);
      }

      function fail() {
        growl.error(gettext('Error loading a poster'));
      }
    }
  }
})();

(function() {
  angular.module('app').factory('vkService', factory);
  factory.$inject = ['growl', 'photoDataservice', 'ratySettings'];

  function factory(growl, photoDataservice, ratySettings) {
    return {
      postToWall: postToWall,
    };

    function postToWall(id) {
      function post(photo) {
        function createWallPostMessage() {
          let text;
          const title = angular.element('#record' + id).data('title');
          const comment = angular.element('#comment' + id)[0].value;
          const ratingTexts = ratySettings.hints;
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
            growl.error(gettext('Error posting to the wall'));
          } else {
            growl.success(gettext('Your post has been posted'));
          }
        });
      }

      function saveWallPhoto(data) {
        VK.api('photos.saveWallPhoto', data, function(response) {
          if (response.error) {
            growl.error(gettext('Error posting a poster to the wall'));
          } else {
            post(response.response[0].id);
          }
        });
      }

      function uploadPhotoToWall(url) {
        photoDataservice.upload(id, url).$promise.then(
          function(response) {
            saveWallPhoto(response.data);
          }
        ).catch(function() {});
      }

      function getWallUploadServerAndUploadPhotoAndPostToWall() {
        VK.api('photos.getWallUploadServer', function(response) {
          if (response.error) {
            growl.error(gettext('Error getting an upload server for wall posting'));
          } else {
            uploadPhotoToWall(response.response.upload_url);
          }
        });
      }

      function hasPoster() {
        return (angular.element('#record' + id).children('.poster').children('img').attr('src').indexOf('no_poster') ===
          -1);
      }

      const rating = parseInt(
        angular.element('#record' + id).children('.details').children('.review').children('.rating').data('rating'));

      if (rating) {
        if (hasPoster()) {
          getWallUploadServerAndUploadPhotoAndPostToWall();
        } else {
          post();
        }
      } else {
        growl.info(gettext('Add a rating to the movie'));
      }
    }
  }
})();

(function() {
  angular.module('app').controller('ListController', ListController);
  ListController.$inject = ['recordDataservice', 'movieCommentDataservice', 'ratingDataservice', 'settingsDataservice',
    'movieDataservice', 'isVkApp', 'ratySettings', 'iconService', 'vkService',
  ];

  function ListController(recordDataservice, movieCommentDataservice, ratingDataservice, settingsDataservice,
    movieDataservice, isVkApp, ratySettings, iconService, vkService) {
    const vm = this;
    vm.openUrl = openUrl;
    vm.removeRecord = removeRecord;
    vm.switchMode = switchMode;
    vm.saveComment = saveComment;
    vm.toggleCommentArea = toggleCommentArea;
    vm.mode = vars.mode;
    vm.isVkApp = isVkApp;
    vm.toggleRecommendation = toggleRecommendation;
    vm.switchSort = switchSort;
    vm.addToList = addToList;
    vm.postToWall = postToWall;

    function postToWall(id) {
      vkService.postToWall(id);
    }

    function addToList(movieId, listId, recordId) {
      movieDataservice.add(movieId, listId, recordId);
    }

    function openUrl(url) {
      location.href = url;
    }

    function removeRecord(id) {
      recordDataservice.delete(id);
    }

    function switchMode(newMode) {
      function deactivateModeMinimal() {
        angular.element('.poster, .comment, .release-date-label, .wall-post').show();
        angular.element('.comment-button').hide();
        angular.element('.details, .imdb-rating, .review, .release-date').css('display', '');
        angular.element('.review').css('padding-top', '10px');
        angular.element('.release-date, .imdb-rating').css({
          'float': '',
          'margin-right': '0',
        });
        angular.element('.movie').removeClass('movie-minimal');
      }
      if (newMode === 'minimal') {
        activateModeMinimal();
      } else {
        deactivateModeMinimal();
      }
      applySettings({
        mode: newMode,
      }, false);
      vm.mode = newMode;
    }

    function saveComment(id) {
      const comment = angular.element('#comment' + id)[0].value;
      movieCommentDataservice.save({
        id: id,
        comment: comment,
      }).$promise.then(
        function() {
          if (!comment) {
            vm.toggleCommentArea(id);
          }
        }
      ).catch(function() {});
    }

    function toggleCommentArea(id) {
      angular.element('#comment-area' + id).toggle();
      angular.element('#comment-area-button' + id).toggle();
      angular.element('#comment' + id).focus();
    }

    function switchSort(value) { // eslint-disable-line no-unused-vars
      let settings = {};
      if (value === 'rating') {
        settings = {
          sort: value,
        };
      } else {
        settings = {
          recommendation: false,
          sort: value,
        };
      }
      applySettings(settings);
    }

    function applySettings(settings, reload = true) {
      settingsDataservice.save(settings).$promise.then(
        function() {
          if (reload) {
            location.reload();
          }
        }
      ).catch(function() {});
    }

    function toggleRecommendation() { // eslint-disable-line no-unused-vars
      if (vars.recommendation) {
        applySettings({
          recommendation: false,
        });
      } else {
        applySettings({
          sort: 'rating',
          recommendation: true,
        });
      }
    }

    function changeRating(id, rating, element) {
      ratingDataservice.save(id, rating, element, ratyCustomSettings);
    }

    function activateModeMinimal() {
      angular.element('.poster, .comment, .comment-button, .release-date-label, .wall-post').hide();
      angular.element('.details, .review').css('display', 'inline');
      angular.element('.review').css('padding-top', '0');
      angular.element('.release-date, .imdb-rating').css({
        'float': 'right',
        'margin-right': '10px',
      });
      angular.element('.movie').addClass('movie-minimal');
    }

    const ratyCustomSettings = {
      readOnly: vars.anothersAccount || vars.listId == 2,
      click: function(score) {
        if (!score) {
          score = 0;
        }
        // eslint-disable-next-line angular/controller-as-vm
        changeRating(angular.element(this).data('record-id'), score, angular.element(this));
      },
    };

    if (vars.mode === 'minimal') {
      activateModeMinimal();
    }

    (function() {
      const settings = angular.extend({}, ratySettings, ratyCustomSettings);
      angular.element('.rating').raty(settings);
    })();

    (function() {
      function setViewedIconsAndRemoveButtons() {
        if (vars.anothersAccount) {
          angular.forEach(angular.element('.movie'),
            function(movie) {
              const id = angular.element(movie).data('id');
              const listId = vars.listData[id]; // eslint-disable-line no-invalid-this
              iconService.setViewedIconAndRemoveButtons(id, listId);
            }
          );
        }
      }

      if (vars.recommendation) {
        angular.element('#button-recommendation').button('toggle');
      }
      setViewedIconsAndRemoveButtons();
      autosize(angular.element('textarea'));
    })();
  }
})();
