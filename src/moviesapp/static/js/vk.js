/* global ratySettings:false */
/* global urlAjaxUploadPosterToWall:false */
/* global VK:false */
// Put VK to globals because we don't want it to be used in other files.

// function initVk() {
//   return VK.callMethod('resizeWindow', 807, $('body').height() + 80);
// };

// setInterval('initVk()', 200);

function inIframe() {
  try {
    return window.self !== window.top;
  } catch (e) {
    return true;
  }
}

function postToWall(id) { // eslint-disable-line no-unused-vars
  function post(photo) {
    function createWallPostMessage() {
      let text;
      const title = $('#record' + id).attr('data-title');
      const comment = $('#comment' + id).val();
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
      const post = {message: createWallPostMessage()};
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
    return $.post(urlAjaxUploadPosterToWall, {
      url: url,
      recordId: id,
    }, function(response) {
      return saveWallPhoto($.parseJSON(response.data));
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
    return $('#record' + id).children('.poster').children('img').attr('src').indexOf('no_poster') === -1;
  }

  const rating = parseInt(
    $('#record' + id).children('.details').children('.review').children('.rating').attr('data-rating'));

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

const isVkApp = inIframe();

if (isVkApp) {
  $('.vk-app-show').show();
  $('#content').addClass('vk');
} else {
  $('.vk-app-hide').show();
}
