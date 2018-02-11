'use strict';

(function() {
  angular.module('app').factory('preferencesService', factory);
  factory.$inject = ['$resource'];

  function factory($resource) {
    return $resource(urls.urlSavePreferences, {}, {
      save: {
        method: 'POST',
      },
    });
  }
})();

(function() {
  angular.module('app').factory('preferencesDataservice', factory);
  factory.$inject = ['preferencesService', 'growl'];

  function factory(preferencesService, growl) {
    return {
      save: save,
    };

    function save(preferences) {
      return preferencesService.save(angular.element.param(preferences), function() {}, fail);

      function fail() {
        growl.error(gettext('Error saving settings'));
      }
    }
  }
})();

(function() {
  angular.module('app').controller('PreferencesController', PreferencesController);
  PreferencesController.$inject = ['preferencesDataservice'];

  function PreferencesController(preferencesDataservice) {
    const vm = this;
    vm.save = save;
    vm.language = vars.language;
    vm.onlyForFriends = vars.onlyForFriends;

    function save(reload) {
      const preferences = {
        language: vm.language,
        onlyForFriends: vm.onlyForFriends,
      };
      preferencesDataservice.save(preferences).$promise.then(function() {
        if (reload) {
          location.reload();
        }
      }).catch(function() {});
    }
  }
})();
