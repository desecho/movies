var ratySettings = {
  path: '/static/bower/raty/lib/images/',
  cancel: true
};

if (language == 'ru') {
  $.extend(ratySettings, {
    hints: ['Ужасно', 'Плохо', 'Нормально', 'Хорошо', 'Отлично'],
    cancelHint: 'Отменить эту оценку',
    noRatedMsg: 'Пока нет оценки',
  });
}

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
