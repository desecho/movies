$(function(){
  const spinnerOptions = {
    lines: 12,
    length: 5,
    width: 3,
    radius: 6,
    corners: 1,
    rotate: 40,
    color: '#000',
    speed: 1,
    trail: 60,
    shadow: false,
    hwaccel: true,
    className: 'spinner',
    zIndex: 2e9,
    top: 'auto',
    left: 'auto'
  }
  $(document).ajaxStart(function(){
    mprogress.start();
  });
  $(document).ajaxStop(function(){
    mprogress.end();
  });
});

var mprogress = new Mprogress();
