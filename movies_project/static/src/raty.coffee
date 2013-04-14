raty_settings =
  hints: ['Ужасно','Плохо','Нормально','Хорошо','Отлично']
  cancelHint: 'Отменить эту оценку'
  noRatedMsg:'Пока нет оценки'
  path: '/static/libs/raty/'
  cancel: true

$ ->
  score_settings =
    score: ->
      $(this).attr('data-rating')
  settings = $.extend({}, raty_settings, raty_custom_settings, score_settings)
  $('.rating').raty(settings)