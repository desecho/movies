'use strict';

(function() {
  angular.module('app').controller('FeedController', FeedController);
  FeedController.$inject = ['ratySettings'];

  function FeedController(ratySettings) {
    const settings = angular.extend({readOnly: true}, ratySettings);
    angular.element('.rating').raty(settings);
  }
})();
