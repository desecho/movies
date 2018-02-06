let ratySettings;

$(function() {
  ratySettings = {
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
    starType : 'i'
  }

  const scoreSettings = {
    score: function() {
      return $(this).attr('data-rating');
    }
  };
  const settings = $.extend({}, ratySettings, ratyCustomSettings, scoreSettings);
  return $('.rating').raty(settings);
});
