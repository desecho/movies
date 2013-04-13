// Generated by CoffeeScript 1.6.2
var raty_settings;

raty_settings = {
  hints: ['ужасно', 'плохо', 'нормально', 'хорошо', 'великолепно'],
  cancelHint: 'Отменить эту оценку',
  noRatedMsg: 'Пока нет оценки',
  path: '/static/libs/raty/',
  cancel: true
};

$(function() {
  var score_settings, settings;

  score_settings = {
    score: function() {
      return $(this).attr('data-rating');
    }
  };
  settings = $.extend({}, raty_settings, raty_custom_settings, score_settings);
  return $('.rating').raty(settings);
});
