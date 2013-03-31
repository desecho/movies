function remove_record_from_page(id) {
  $('#record' + id).fadeOut('fast', function() {
    $(this).remove();
    check_if_no_records();
  });
}

function add_to_list(movie_id, list_id, record_id) {
  $.post(url_ajax_add_to_list, {'movie_id': movie_id, 'list_id': list_id},
        function(data) {
          set_viewed_icon_and_remove_buttons(record_id, list_id);
        }
  ).error(function() {
      displayError('Ошибка добавления фильма в список.');
  });
}

function check_if_no_records() {
  if (!$('.movie').length) {
    $('#results').html('Список пуст.');
  }
}

function set_viewed_icon_and_remove_buttons(record_id, list_id) {
  function remove_buttons(){
    $('#record' + record_id).children('.buttons').html('');
  }
  set_viewed_icon(record_id, list_id);
  if (list_id !== 0) {
    remove_buttons();
  }
}

function set_viewed_icon(record_id, list_id) {
  var icon;
  if (list_id === 0) {
    return;
  }
  if (list_id == 1) {
    icon = 'open';
    title = 'Просмотрено';
  }
  if (list_id == 2) {
    icon = 'close';
    title = 'К просмотру';
  }
  var html = '<i class="icon-eye-' + icon + '" title="' + title + '"></i>';
  $('#record' + record_id).children('.title').prepend(html);
}

function show_torrents(query) {
  function get_torrents(query) {
    function bytes_to_size(bytes, precision) {
      var kilobyte = 1024;
      var megabyte = kilobyte * 1024;
      var gigabyte = megabyte * 1024;
      var terabyte = gigabyte * 1024;
      if ((bytes >= 0) && (bytes < kilobyte)) {
        return bytes + ' B';
      } else if ((bytes >= kilobyte) && (bytes < megabyte)) {
        return (bytes / kilobyte).toFixed(precision) + ' KB';
      } else if ((bytes >= megabyte) && (bytes < gigabyte)) {
        return (bytes / megabyte).toFixed(precision) + ' MB';
      } else if ((bytes >= gigabyte) && (bytes < terabyte)) {
        return (bytes / gigabyte).toFixed(precision) + ' GB';
      } else if (bytes >= terabyte) {
        return (bytes / terabyte).toFixed(precision) + ' TB';
      } else {
        return bytes + ' B';
      }
    }
    $.ajax({
      type: "POST",
      url: url_ajax_download,
      data: {'query': query},
      success: function(json) {
          json = $.parseJSON(json.data);
          var total_lists = json.items.list.length;
          if (total_lists === 0) {
              $("#torrents").html('Торрентов не найдено.');
          } else {
            html = '<ul>';
            for (var i = 0; i < total_lists; i++) {
              html += '<li id="searchresult-' + i + '"><a href="' + json.items.list[i].uri + '" target="_blank">' + json.items.list[i].title + '</a> &#8593; ' + json.items.list[i].Seeds + ' &#8595; ' + json.items.list[i].leechers + '<br>' + json.items.list[i].tracker + ' &mdash; ' + bytes_to_size(json.items.list[i].size, 2) + ' &mdash; ' + json.items.list[i].regtime + '</li>'
            }
            html += '</ul>';
            $("#torrents").html(html);
          }
        },
      async: false
    }).error(function() {
      displayError('Ошибка поиска торрентов.');
    });
  }
  get_torrents(query);
  $('#myModal').modal('toggle');
}