raty_settings =
  hints: ['ужасно','плохо','нормально','хорошо','великолепно']
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