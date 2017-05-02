$(function(){
  $(document).ajaxStart(function(){
    mprogress.start();
  });
  $(document).ajaxStop(function(){
    mprogress.end();
  });
});

var mprogress = new Mprogress();
