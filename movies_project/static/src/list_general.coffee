remove_record_from_page = (id) ->
  $('#record' + id).fadeOut('fast', ->
    $(this).remove()
    check_if_no_records()
  )

add_to_list = (movie_id, list_id, record_id) ->
  $.post(url_ajax_add_to_list,
    movie_id: movie_id
    list_id: list_id,
    (data) ->
      set_viewed_icon_and_remove_buttons(record_id, list_id)
  ).error ->
    displayError 'Ошибка добавления фильма в список.'

check_if_no_records = ->
  if not $('.movie').length
    $('#results').html 'Список пуст.'

set_viewed_icon_and_remove_buttons = (record_id, list_id) ->
  remove_buttons = ->
    $('#record' + record_id).children('.buttons').html ''
  set_viewed_icon(record_id, list_id)
  if list_id isnt 0
    remove_buttons()

set_viewed_icon = (record_id, list_id) ->
  if list_id is 0
    return
  else if list_id  is 1
    icon = 'open'
    title = 'Просмотрено'
  else if list_id is 2
    icon = 'close'
    title = 'К просмотру'
  html = '<i class="icon-eye-' + icon + '" title="' + title + '"></i>'
  $('#record' + record_id).children('.title').prepend(html)

show_torrents = (query) ->
  get_torrents = (query) ->
    bytes_to_size = (bytes, precision) ->
      kilobyte = 1024
      megabyte = kilobyte * 1024
      gigabyte = megabyte * 1024
      terabyte = gigabyte * 1024
      if (bytes >= 0) and (bytes < kilobyte)
        bytes + ' B'
      else if (bytes >= kilobyte) and (bytes < megabyte)
        (bytes / kilobyte).toFixed(precision) + ' KB'
      else if (bytes >= megabyte) and (bytes < gigabyte)
        (bytes / megabyte).toFixed(precision) + ' MB'
      else if (bytes >= gigabyte) and (bytes < terabyte)
        (bytes / gigabyte).toFixed(precision) + ' GB'
      else if bytes >= terabyte
        (bytes / terabyte).toFixed(precision) + ' TB'
      else
        bytes + ' B'
    $.ajax(
      type: 'POST'
      url: url_ajax_download
      data:
        query: query
      success: (json) ->
        json = $.parseJSON(json.data)
        total_lists = json.items.list.length
        if total_lists is 0
          $("#torrents").html 'Торрентов не найдено.'
        else
          html = '<ul>'
          i = 0
          while i < total_lists
            html += '<li id="searchresult-' + i + '"><a href="' + json.items.list[i].uri + '" target="_blank">' +
                    json.items.list[i].title + '</a> &#8593; ' + json.items.list[i].Seeds + ' &#8595; ' +
                    json.items.list[i].leechers + '<br>' + json.items.list[i].tracker + ' &mdash; ' +
                    bytes_to_size(json.items.list[i].size, 2) + ' &mdash; ' + json.items.list[i].regtime + '</li>'
            i++
          html += '</ul>'
          $("#torrents").html(html)
      ,
      async: false
    ).error ->
      displayError 'Ошибка поиска торрентов.'
  get_torrents(query)
  $('#myModal').modal('toggle')
  undefined