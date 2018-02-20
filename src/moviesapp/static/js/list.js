webpackJsonp([3],{

/***/ 38:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* WEBPACK VAR INJECTION */(function($, autosize) {/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_vue__ = __webpack_require__(2);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_vue___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_vue__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_axios__ = __webpack_require__(4);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_axios___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_axios__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__helpers__ = __webpack_require__(8);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__list_helpers__ = __webpack_require__(14);
/* global VK:false */
/* global autosize:false */









function activateModeMinimal() {
  $('.poster, .comment, .comment-button, .release-date-label').hide();
  $('.details, .review').css('display', 'inline');
  $('.review').css('padding-top', '0');
  $('.release-date, .imdb-rating').css({
    'float': 'right',
    'margin-right': '10px',
  });
  $('.movie').addClass('movie-minimal');
}

function changeRating(id, rating, element) {
  function success() {
    element.data('rating', rating);
  }

  function fail() {
    function revertToPreviousRating(element) {
      const scoreSettings = {
        score: element.data('rating'),
      };
      const settings = $.extend({}, vars.ratySettings, ratyCustomSettings, scoreSettings);
      element.raty(settings);
    }

    revertToPreviousRating(element);
    __WEBPACK_IMPORTED_MODULE_0_vue___default.a.prototype.$flashStorage.flash(gettext('Error adding a rating'), 'error', vars.flashOptions);
  }

  const url = urls.urlChangeRating + id + '/';
  const data = $.param({
    rating: rating,
  });
  __WEBPACK_IMPORTED_MODULE_1_axios___default.a.put(url, data).then(success).catch(fail);
}

function applySettings(settings, reload = true) {
  const data = {
    settings: JSON.stringify(settings),
  };
  __WEBPACK_IMPORTED_MODULE_1_axios___default.a.put(urls.urlSaveSettings, $.param(data)).then(function() {
    if (reload) {
      location.reload();
    }
  }).catch(function() {
    __WEBPACK_IMPORTED_MODULE_0_vue___default.a.prototype.$flashStorage.flash(gettext('Error applying the settings'), 'error', vars.flashOptions);
  });
}

function setViewedIconsAndRemoveButtons() {
  if (vars.anothersAccount) {
    $('.movie').each(function() {
      const id = $(this).data('id'); // eslint-disable-line no-invalid-this
      const listId = vars.listData[id];
      Object(__WEBPACK_IMPORTED_MODULE_3__list_helpers__["b" /* setViewedIconAndRemoveButtons */])(id, listId);
    });
  }
}

window.vm = new __WEBPACK_IMPORTED_MODULE_0_vue___default.a({
  el: '#app',
  data: {
    sortByDate: false,
    mode: vars.mode,
    isVkApp: vars.isVkApp,
  },
  methods: {
    openUrl: function(url) {
      location.href = url;
    },
    retinajs: __WEBPACK_IMPORTED_MODULE_2__helpers__["a" /* retina */],
    switchMode: function switchMode(newMode) {
      function deactivateModeMinimal() {
        $('.poster, .comment, .release-date-label').show();
        $('.comment-button').hide();
        $('.details, .imdb-rating, .review, .release-date').css('display', '');
        $('.review').css('padding-top', '10px');
        $('.release-date, .imdb-rating').css({
          'float': '',
          'margin-right': '0',
        });
        $('.movie').removeClass('movie-minimal');
      }
      if (newMode === 'minimal') {
        activateModeMinimal();
      } else {
        deactivateModeMinimal();
      }
      applySettings({
        mode: newMode,
      }, false);
      vm.mode = newMode;
    },
    toggleRecommendation: function() {
      const newRecommendationSetting = !vars.recommendation;
      const settings = {
        recommendation: newRecommendationSetting,
      };
      if (newRecommendationSetting) {
        settings.sort = 'rating';
      }
      applySettings(settings);
    },
    switchSort: function(value) {
      const settings = {
        sort: value,
      };
      if (value !== 'rating') {
        settings.recommendation = false;
      }
      applySettings(settings);
    },
    removeRecord: function(id) {
      function success() {
        function removeRecordFromPage(id) {
          $('#record' + id).fadeOut('fast', function() {
            $(this).remove(); // eslint-disable-line no-invalid-this
          });
        }
        removeRecordFromPage(id);
      }

      function fail() {
        vm.flash(gettext('Error removing the movie'), 'error', vars.flashOptions);
      }

      const url = urls.urlRemoveRecord + id + '/';
      __WEBPACK_IMPORTED_MODULE_1_axios___default.a.delete(url).then(success).catch(fail);
    },
    postToWall: function(id) {
      const vm = this;

      function post(photo) {
        function createWallPostMessage() {
          let text;
          const title = $('#record' + id).data('title');
          const comment = $('#comment' + id)[0].value;
          const ratingTexts = vars.ratySettings.hints;
          const ratingPost = ratingTexts[rating - 1];
          if (rating > 2) {
            text = gettext('I recommend watching');
          } else {
            text = gettext('I don\'t recommend watching');
          }
          const myRating = gettext('My rating');
          text += ` "${title}".\n${myRating} - ${ratingPost}.`;
          if (comment) {
            text += '\n' + comment;
          }
          return text;
        }

        function createWallPost() {
          const post = {
            message: createWallPostMessage(),
          };
          if (photo) {
            post.attachments = photo;
          }
          return post;
        }

        VK.api('wall.post', createWallPost(), function(response) {
          if (response.error) {
            // error_msg: "Operation denied by user"
            if (response.error.error_code === 10007) {
              return;
            }
            vm.flash(gettext('Error posting to the wall'), 'error', vars.flashOptions);
          } else {
            vm.flash(gettext('Your post has been posted'), 'success', vars.flashOptions);
          }
        });
      }

      function saveWallPhoto(data) {
        VK.api('photos.saveWallPhoto', data, function(response) {
          if (response.error) {
            vm.flash(gettext('Error posting a poster to the wall'), 'error', vars.flashOptions);
          } else {
            post(response.response[0].id);
          }
        });
      }

      function uploadPhotoToWall(uploadUrl) {
        const url = urls.urlUploadPosterToWall + id + '/';
        __WEBPACK_IMPORTED_MODULE_1_axios___default.a.post(url, $.param({
          url: uploadUrl,
        })).then(function(response) {
          const data = JSON.parse(response.data.data);
          saveWallPhoto(data);
        }).catch(function() {
          vm.flash(gettext('Error loading a poster'), 'error', vars.flashOptions);
        });
      }

      function getWallUploadServerAndUploadPhotoAndPostToWall() {
        VK.api('photos.getWallUploadServer', function(response) {
          if (response.error) {
            vm.flash(gettext('Error getting an upload server for wall posting'), 'error', vars.flashOptions);
          } else {
            uploadPhotoToWall(response.response.upload_url);
          }
        });
      }

      function hasPoster() {
        return ($('#record' + id).children('.poster').children('img').attr('src').indexOf('no_poster') ===
          -1);
      }

      const rating = $('#record' + id).children('.details').children('.review').children('.rating').data('rating');

      if (rating) {
        if (hasPoster()) {
          getWallUploadServerAndUploadPhotoAndPostToWall();
        } else {
          post();
        }
      } else {
        vm.flash(gettext('Add a rating to the movie'), 'info', vars.flashOptions);
      }
    },
    addToList: __WEBPACK_IMPORTED_MODULE_3__list_helpers__["a" /* addToList */],
    toggleCommentArea: function(id) {
      $('#comment-area' + id).toggle();
      $('#comment-area-button' + id).toggle();
      $('#comment' + id).focus();
    },
    saveComment: function(id) {
      const comment = $('#comment' + id)[0].value;
      const data = $.param({
        id: id,
        comment: comment,
      });
      __WEBPACK_IMPORTED_MODULE_1_axios___default.a.put(urls.urlSaveComment, data).then(function() {
        if (!comment) {
          vm.toggleCommentArea(id);
        }
      }).catch(function() {
        vm.flash(gettext('Error saving a comment'), 'error', vars.flashOptions);
      });
    },
  },
});

const ratyCustomSettings = {
  readOnly: vars.anothersAccount || vars.listId == 2,
  click: function(score) {
    if (!score) {
      score = 0;
    }
    changeRating($(this).data('record-id'), score, $(this));
  },
};

if (vars.mode === 'minimal') {
  activateModeMinimal();
}

(function() {
  const settings = $.extend({}, vars.ratySettings, ratyCustomSettings);
  $('.rating').raty(settings);
})();

if (vars.recommendation) {
  $('#button-recommendation').button('toggle');
}

setViewedIconsAndRemoveButtons();
autosize($('textarea'));

/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__(1), __webpack_require__(39)))

/***/ }),

/***/ 39:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_FACTORY__, __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/*!
	Autosize 4.0.0
	license: MIT
	http://www.jacklmoore.com/autosize
*/
(function (global, factory) {
	if (true) {
		!(__WEBPACK_AMD_DEFINE_ARRAY__ = [exports, module], __WEBPACK_AMD_DEFINE_FACTORY__ = (factory),
				__WEBPACK_AMD_DEFINE_RESULT__ = (typeof __WEBPACK_AMD_DEFINE_FACTORY__ === 'function' ?
				(__WEBPACK_AMD_DEFINE_FACTORY__.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__)) : __WEBPACK_AMD_DEFINE_FACTORY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
	} else if (typeof exports !== 'undefined' && typeof module !== 'undefined') {
		factory(exports, module);
	} else {
		var mod = {
			exports: {}
		};
		factory(mod.exports, mod);
		global.autosize = mod.exports;
	}
})(this, function (exports, module) {
	'use strict';

	var map = typeof Map === "function" ? new Map() : (function () {
		var keys = [];
		var values = [];

		return {
			has: function has(key) {
				return keys.indexOf(key) > -1;
			},
			get: function get(key) {
				return values[keys.indexOf(key)];
			},
			set: function set(key, value) {
				if (keys.indexOf(key) === -1) {
					keys.push(key);
					values.push(value);
				}
			},
			'delete': function _delete(key) {
				var index = keys.indexOf(key);
				if (index > -1) {
					keys.splice(index, 1);
					values.splice(index, 1);
				}
			}
		};
	})();

	var createEvent = function createEvent(name) {
		return new Event(name, { bubbles: true });
	};
	try {
		new Event('test');
	} catch (e) {
		// IE does not support `new Event()`
		createEvent = function (name) {
			var evt = document.createEvent('Event');
			evt.initEvent(name, true, false);
			return evt;
		};
	}

	function assign(ta) {
		if (!ta || !ta.nodeName || ta.nodeName !== 'TEXTAREA' || map.has(ta)) return;

		var heightOffset = null;
		var clientWidth = ta.clientWidth;
		var cachedHeight = null;

		function init() {
			var style = window.getComputedStyle(ta, null);

			if (style.resize === 'vertical') {
				ta.style.resize = 'none';
			} else if (style.resize === 'both') {
				ta.style.resize = 'horizontal';
			}

			if (style.boxSizing === 'content-box') {
				heightOffset = -(parseFloat(style.paddingTop) + parseFloat(style.paddingBottom));
			} else {
				heightOffset = parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
			}
			// Fix when a textarea is not on document body and heightOffset is Not a Number
			if (isNaN(heightOffset)) {
				heightOffset = 0;
			}

			update();
		}

		function changeOverflow(value) {
			{
				// Chrome/Safari-specific fix:
				// When the textarea y-overflow is hidden, Chrome/Safari do not reflow the text to account for the space
				// made available by removing the scrollbar. The following forces the necessary text reflow.
				var width = ta.style.width;
				ta.style.width = '0px';
				// Force reflow:
				/* jshint ignore:start */
				ta.offsetWidth;
				/* jshint ignore:end */
				ta.style.width = width;
			}

			ta.style.overflowY = value;
		}

		function getParentOverflows(el) {
			var arr = [];

			while (el && el.parentNode && el.parentNode instanceof Element) {
				if (el.parentNode.scrollTop) {
					arr.push({
						node: el.parentNode,
						scrollTop: el.parentNode.scrollTop
					});
				}
				el = el.parentNode;
			}

			return arr;
		}

		function resize() {
			var originalHeight = ta.style.height;
			var overflows = getParentOverflows(ta);
			var docTop = document.documentElement && document.documentElement.scrollTop; // Needed for Mobile IE (ticket #240)

			ta.style.height = '';

			var endHeight = ta.scrollHeight + heightOffset;

			if (ta.scrollHeight === 0) {
				// If the scrollHeight is 0, then the element probably has display:none or is detached from the DOM.
				ta.style.height = originalHeight;
				return;
			}

			ta.style.height = endHeight + 'px';

			// used to check if an update is actually necessary on window.resize
			clientWidth = ta.clientWidth;

			// prevents scroll-position jumping
			overflows.forEach(function (el) {
				el.node.scrollTop = el.scrollTop;
			});

			if (docTop) {
				document.documentElement.scrollTop = docTop;
			}
		}

		function update() {
			resize();

			var styleHeight = Math.round(parseFloat(ta.style.height));
			var computed = window.getComputedStyle(ta, null);

			// Using offsetHeight as a replacement for computed.height in IE, because IE does not account use of border-box
			var actualHeight = computed.boxSizing === 'content-box' ? Math.round(parseFloat(computed.height)) : ta.offsetHeight;

			// The actual height not matching the style height (set via the resize method) indicates that
			// the max-height has been exceeded, in which case the overflow should be allowed.
			if (actualHeight !== styleHeight) {
				if (computed.overflowY === 'hidden') {
					changeOverflow('scroll');
					resize();
					actualHeight = computed.boxSizing === 'content-box' ? Math.round(parseFloat(window.getComputedStyle(ta, null).height)) : ta.offsetHeight;
				}
			} else {
				// Normally keep overflow set to hidden, to avoid flash of scrollbar as the textarea expands.
				if (computed.overflowY !== 'hidden') {
					changeOverflow('hidden');
					resize();
					actualHeight = computed.boxSizing === 'content-box' ? Math.round(parseFloat(window.getComputedStyle(ta, null).height)) : ta.offsetHeight;
				}
			}

			if (cachedHeight !== actualHeight) {
				cachedHeight = actualHeight;
				var evt = createEvent('autosize:resized');
				try {
					ta.dispatchEvent(evt);
				} catch (err) {
					// Firefox will throw an error on dispatchEvent for a detached element
					// https://bugzilla.mozilla.org/show_bug.cgi?id=889376
				}
			}
		}

		var pageResize = function pageResize() {
			if (ta.clientWidth !== clientWidth) {
				update();
			}
		};

		var destroy = (function (style) {
			window.removeEventListener('resize', pageResize, false);
			ta.removeEventListener('input', update, false);
			ta.removeEventListener('keyup', update, false);
			ta.removeEventListener('autosize:destroy', destroy, false);
			ta.removeEventListener('autosize:update', update, false);

			Object.keys(style).forEach(function (key) {
				ta.style[key] = style[key];
			});

			map['delete'](ta);
		}).bind(ta, {
			height: ta.style.height,
			resize: ta.style.resize,
			overflowY: ta.style.overflowY,
			overflowX: ta.style.overflowX,
			wordWrap: ta.style.wordWrap
		});

		ta.addEventListener('autosize:destroy', destroy, false);

		// IE9 does not fire onpropertychange or oninput for deletions,
		// so binding to onkeyup to catch most of those events.
		// There is no way that I know of to detect something like 'cut' in IE9.
		if ('onpropertychange' in ta && 'oninput' in ta) {
			ta.addEventListener('keyup', update, false);
		}

		window.addEventListener('resize', pageResize, false);
		ta.addEventListener('input', update, false);
		ta.addEventListener('autosize:update', update, false);
		ta.style.overflowX = 'hidden';
		ta.style.wordWrap = 'break-word';

		map.set(ta, {
			destroy: destroy,
			update: update
		});

		init();
	}

	function destroy(ta) {
		var methods = map.get(ta);
		if (methods) {
			methods.destroy();
		}
	}

	function update(ta) {
		var methods = map.get(ta);
		if (methods) {
			methods.update();
		}
	}

	var autosize = null;

	// Do nothing in Node.js environment and IE8 (or lower)
	if (typeof window === 'undefined' || typeof window.getComputedStyle !== 'function') {
		autosize = function (el) {
			return el;
		};
		autosize.destroy = function (el) {
			return el;
		};
		autosize.update = function (el) {
			return el;
		};
	} else {
		autosize = function (el, options) {
			if (el) {
				Array.prototype.forEach.call(el.length ? el : [el], function (x) {
					return assign(x, options);
				});
			}
			return el;
		};
		autosize.destroy = function (el) {
			if (el) {
				Array.prototype.forEach.call(el.length ? el : [el], destroy);
			}
			return el;
		};
		autosize.update = function (el) {
			if (el) {
				Array.prototype.forEach.call(el.length ? el : [el], update);
			}
			return el;
		};
	}

	module.exports = autosize;
});

/***/ })

},[38]);