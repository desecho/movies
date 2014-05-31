$('input').change ->
  $.post(url_ajax_save_preferences, {
        lang: $('input:radio[name=lang]:checked').val(),
        only_for_friends: $('input[name=only_for_friends]:checked').val()}).error ->
    display_message 'Ошибка сохранения настроек'