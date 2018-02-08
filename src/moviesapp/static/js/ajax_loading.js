/* global Mprogress:false */
// Put Mprogress to globals because we don't want it to be used in other files.

$(document).ajaxStart(function() {
  mprogress.start();
});

$(document).ajaxStop(function() {
  mprogress.end();
});

const mprogress = new Mprogress();
