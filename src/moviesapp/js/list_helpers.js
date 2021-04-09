'use strict';

import axios from 'axios';


export function addToList(movieId, listId, recordId) {
  const url = urls.addToList + movieId + '/';
  axios.post(url, $.param({
    listId: listId,
  })).then(function() {
    setViewedIconAndRemoveButtons(recordId, listId);
  }).catch(function() {
    vm.flashError(gettext('Error adding the movie to the list'));
  });
}


export function setViewedIconAndRemoveButtons(recordId, listId) {
  function removeButtons() {
    return $('#record' + recordId).children('.title').children('.add-to-list-buttons').remove();
  }

  function setViewedIcon(recordId, listId) {
    let icon;
    let title;

    if (listId === 0) {
      return;
    } else if (listId === 1) {
      icon = '';
      title = gettext('Watched');
    } else if (listId === 2) {
      icon = '-slash';
      title = gettext('To Watch');
    }
    const html = ` <i class="fa fa-eye${icon}" title=${title}></i> `;
    return $('#record' + recordId).children('.title').prepend(html);
  }

  setViewedIcon(recordId, listId);
  if (listId !== 0) {
    return removeButtons();
  }
}
