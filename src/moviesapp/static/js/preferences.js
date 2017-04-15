app.factory('SavePreferences', ['$resource', function($resource) {
  return $resource(urlSavePreferences, {}, {
    post: {method: 'POST', headers: headers}
  });
}]);

app.controller('PreferencesController', ['$scope', 'SavePreferences',
function ($scope, SavePreferences) {
  $scope.savePreferences = function(){
    const preferences = {language: $('input:radio[name=lang]:checked').val()};
    if (typeof vk !== undefined) {
      preferences.onlyForFriends = $('input[name=only_for_friends]:checked').val();
    }
    SavePreferences.post($.param(preferences), function(){
      location.reload();
    }, function(){
      displayMessage(gettext('Error saving settings'));
    });
  }
}]);