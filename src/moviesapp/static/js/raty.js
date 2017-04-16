var ratySettings = {
  path: '/static/bower/raty/lib/images/',
  cancel: true
};

$.extend(ratySettings, {
  hints: [
    gettext('Awful'),
    gettext('Bad'),
    gettext('Regular'),
    gettext('Good'),
    gettext('Awesome'),
  ],
  cancelHint: gettext('Cancel rating'),
  noRatedMsg: gettext('No rating yet'),
});

$(function() {
  var scoreSettings, settings;
  scoreSettings = {
    score: function() {
      return $(this).attr('data-rating');
    }
  };
  settings = $.extend({}, ratySettings, ratyCustomSettings, scoreSettings);
  return $('.rating').raty(settings);
});
