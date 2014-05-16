$('input').change ->
  $.post(url_ajax_save_preferences, {titles: $('input:radio[name=titles]:checked').val()}).error ->
    display_message 'Ошибка сохранения настроек'