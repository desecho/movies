$(function(){
  $("#password-change").submit(function(e){
    e.preventDefault();
    $('#new_password2').val($('#new_password1').val());
    $('#password-change')[0].submit();
  });
});
