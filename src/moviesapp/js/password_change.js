'use strict';

$('#password-change').submit(function(e) {
  e.preventDefault();
  const password = $('#new_password1')[0].value;
  $('#new_password2').value = password;
  $('#password-change')[0].submit();
});
