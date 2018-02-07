$(function(){
  $("#registration").submit(function(e){
    e.preventDefault();
    $('#password2').val($('#password1').val());
    $('#registration')[0].submit();
  });
});
