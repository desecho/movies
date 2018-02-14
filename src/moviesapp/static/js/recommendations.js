'use strict';

(function() {
  angular.module('app').controller('RecommendationsController', RecommendationsController);
  RecommendationsController.$inject = ['ratySettings'];

  function RecommendationsController(ratySettings) {
    const settings = angular.extend({readOnly: true}, ratySettings);
    angular.element('.rating').raty(settings);
  }
})();
