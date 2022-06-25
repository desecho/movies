'use strict';

$('#registration').on('submit', function(e) {
  e.preventDefault();
  const password = $('#password1')[0].value;
  $('#password2')[0].value = password;
  $('#registration')[0].submit();
});
