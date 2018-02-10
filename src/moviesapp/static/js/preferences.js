'use strict';

(function() {
  createPostResource('savePreferences', urls.urlSavePreferences);
  angular.module('app').controller('PreferencesController', PreferencesController);
  PreferencesController.$inject = ['savePreferences'];

  function PreferencesController(savePreferences) {
    let vm = this;
    vm.save = save;
    vm.language = vars.language;
    vm.onlyForFriends = vars.onlyForFriends;

    function save(reload) {
      const preferences = {
        language: vm.language,
        onlyForFriends: vm.onlyForFriends
      };
      savePreferences.post(angular.element.param(preferences), function() {
        if (reload) {
          location.reload();
        }
      }, function() {
        displayMessage(gettext('Error saving settings'));
      });
    }
  }
})();
