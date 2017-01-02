function addToList(movieId, listId, recordId) {
  return $.post(urlAddToList, {
    movieId: movieId,
    listId: listId
  }, function(data) {
    return setViewedIconAndRemoveButtons(recordId, listId);
  }).error(function() {
    return displayMessage(gettext('Error adding the movie to the list'));
  });
};

function setViewedIconAndRemoveButtons(recordId, listId) {
  function removeButtons() {
    return $('#record' + recordId).children('.title').children('.add-to-list-buttons').html('');
  };

  setViewedIcon(recordId, listId);
  if (listId !== 0) {
    return removeButtons();
  }
};

function setViewedIcon(recordId, listId) {
  var html, icon, title;
  if (listId === 0) {
    return;
  } else if (listId === 1) {
    icon = '';
    title = gettext('Watched');
  } else if (listId === 2) {
    icon = '-slash';
    title = gettext('To Watch');
  }
  html = " <i class=\"fa fa-eye" + icon + "\" title=\"" + title + "\"></i> ";
  return $('#record' + recordId).children('.title').prepend(html);
};
