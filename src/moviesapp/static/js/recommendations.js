'use strict';

(function() {
  angular.module('app').controller('RecommendationsController', RecommendationsController);
  RecommendationsController.$inject = ['ratySettings', 'movieDataservice'];

  function RecommendationsController(ratySettings, movieDataservice) {
    const vm = this;
    vm.addToList = addToList;

    function addToList(movieId, listId, recordId) {
      movieDataservice.add(movieId, listId, recordId);
    }

    (function() {
      const settings = angular.extend({
        readOnly: true,
      }, ratySettings);
      angular.element('.rating').raty(settings);
    })();
  }
})();
