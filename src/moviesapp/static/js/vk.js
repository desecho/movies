/* global ratySettings:false */
/* global VK:false */

'use strict';

function postToWall(id) { // eslint-disable-line no-unused-vars
  function post(photo) {
    function createWallPostMessage() {
      let text;
      const title = angular.element('#record' + id).data('title');
      const comment = angular.element('#comment' + id)[0].value;
      const ratingPost = ratySettings['hints'][rating - 1];
      if (rating > 2) {
        text = gettext('I recommend watching');
      } else {
        text = gettext('I don\'t recommend watching');
      }
      const myRating = gettext('My rating');
      text += ` "${title}".
${myRating} - ${ratingPost}.`;
      if (comment) {
        text += '\n ' + comment;
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

    return VK.api('wall.post', createWallPost(), function(response) {
      if (response.error) {
        return displayMessage(gettext('Error posting to the wall'));
      } else {
        return displayMessage(gettext('Your post has been posted'));
      }
    });
  }

  function saveWallPhoto(data) {
    return VK.api('photos.saveWallPhoto', data, function(response) {
      if (response.error) {
        return displayMessage(gettext('Error posting a poster to the wall'));
      } else {
        return post(response.response[0].id);
      }
    });
  }

  function uploadPhotoToWall(url) {
    return $.post(urls.urlAjaxUploadPosterToWall, {
      url: url,
      recordId: id,
    }, function(response) {
      return saveWallPhoto(angular.fromJson(response.data));
    }).fail(function() {
      return displayMessage(gettext('Error loading a poster'));
    });
  }

  function getWallUploadServerAndUploadPhotoAndPostToWall() {
    return VK.api('photos.getWallUploadServer', function(response) {
      if (response.error) {
        return displayMessage(gettext('Error getting an upload server for wall posting'));
      } else {
        return uploadPhotoToWall(response.response.upload_url);
      }
    });
  }

  function hasPoster() {
    return angular.element('#record' + id).children('.poster').children('img').attr('src').indexOf('no_poster') === -1;
  }

  const rating = parseInt(
    angular.element('#record' + id).children('.details').children('.review').children('.rating').data('rating'));

  if (rating) {
    if (hasPoster()) {
      return getWallUploadServerAndUploadPhotoAndPostToWall();
    } else {
      return post();
    }
  } else {
    return displayMessage(gettext('Add a rating to the movie'));
  }
}
