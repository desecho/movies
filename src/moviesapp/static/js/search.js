webpackJsonp([4],{

/***/ 19:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($) {/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_vue__ = __webpack_require__(2);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_vue___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_vue__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_axios__ = __webpack_require__(4);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_axios___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_axios__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__helpers__ = __webpack_require__(8);







String.prototype.toTitleCase = function() { // eslint-disable-line no-extend-native
  return this.replace(/\w\S*/g, function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
};

window.vm = new __WEBPACK_IMPORTED_MODULE_0_vue___default.a({
  el: '#app',
  data: {
    searchType: gettext('Movie'),
    searchTypeCode: 'movie',
    language: vars.language,
    query: '',
    movies: [],
    popularOnly: true,
    sortByDate: false,
  },
  methods: {
    search: function() {
      const options = {
        popularOnly: vm.popularOnly,
        sortByDate: vm.sortByDate,
      };
      const data = {
        query: vm.query,
        type: vm.searchTypeCode,
        options: $.param(options),
      };
      const url = urls.urlSearchMovie + '?' + $.param(data);
      __WEBPACK_IMPORTED_MODULE_1_axios___default.a.get(url).then(function(response) {
        if (response.data.movies.length === 0) {
          vm.flash(gettext('Nothing has been found'), 'info', vars.flashOptions);
        }
        vm.movies = response.data.movies;
      }).catch(function() {
        vm.flash(gettext('Search Error'), 'error', vars.flashOptions);
      });
    },
    retinajs: __WEBPACK_IMPORTED_MODULE_2__helpers__["a" /* retina */],
    addToListFromDb: function(movieId, listId) {
      const movie = $('#movie' + movieId);
      movie.fadeOut('fast');
      const data = {
        movieId: movieId,
        listId: listId,
      };
      __WEBPACK_IMPORTED_MODULE_1_axios___default.a.post(urls.urlAddToListFromDb, $.param(data)).then(function(response) {
        if (response.data.status === 'not_found') {
          vm.flash(gettext('Movie is not found in the database'), 'error', vars.flashOptions);
        }
      }).catch(function() {
        vm.flash(gettext('Error adding a movie'), 'error', vars.flashOptions);
      });
    },
    changeSearchType: function(code) {
      vm.searchTypeCode = code;
      vm.searchType = gettext(code.toTitleCase());
    },
  },
});

/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(1)))

/***/ })

},[19]);