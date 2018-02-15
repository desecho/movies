'use strict';

function setViewedIconAndRemoveButtons(recordId, listId) {
  function removeButtons() {
    return angular.element('#record' + recordId).children('.title').children('.add-to-list-buttons').remove();
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
    return angular.element('#record' + recordId).children('.title').prepend(html);
  }

  setViewedIcon(recordId, listId);
  if (listId !== 0) {
    return removeButtons();
  }
}
