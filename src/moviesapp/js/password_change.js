'use strict';

$('#password-change').submit(function(e) {
  e.preventDefault();
  const password = $('#new_password1').val();
  $('#new_password2').val(password);
  $('#password-change')[0].submit();
});
