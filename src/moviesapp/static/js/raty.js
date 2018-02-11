/* global ratyCustomSettings:false */

'use strict';

let ratySettings = {
  hints: [
    gettext('Awful'),
    gettext('Bad'),
    gettext('Regular'),
    gettext('Good'),
    gettext('Awesome'),
  ],
  cancelHint: gettext('Cancel rating'),
  noRatedMsg: gettext('No rating yet'),
  cancel: true,
  starType: 'i',
};

(function() {
  const scoreSettings = {
    score: function() {
      return angular.element(this).attr('data-rating');
    },
  };
  const settings = angular.extend({}, ratySettings, ratyCustomSettings, scoreSettings);
  angular.element('.rating').raty(settings);
})();
