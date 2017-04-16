app.factory('SavePreferences', ['$resource', function($resource) {
  return $resource(urlSavePreferences, {}, {
    post: {method: 'POST', headers: headers}
  });
}]);

app.controller('PreferencesController', ['$scope', 'SavePreferences',
function ($scope, SavePreferences) {
  $scope.savePreferences = function(reload){
    const preferences = {language: $('input:radio[name=lang]:checked').val()};
    var field = $('input[name=only_for_friends]');
    if (field.length !== 0) {
      preferences.onlyForFriends = field.prop('checked');
    }
    SavePreferences.post($.param(preferences), function(){
      console.log(reload)
      if (reload) {
        location.reload();
      }
    }, function(){
      displayMessage(gettext('Error saving settings'));
    });
  }
}]);