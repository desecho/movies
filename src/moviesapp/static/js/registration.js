webpackJsonp([5],{

/***/ 41:
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function($) {

$('#registration').submit(function(e) {
  e.preventDefault();
  const password = $('#password1')[0].value;
  $('#password2')[0].value = password;
  $('#registration')[0].submit();
});

/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1)))

/***/ })

},[41]);