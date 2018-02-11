'use strict';

angular.element('#registration').submit(function(e) {
  e.preventDefault();
  const password = angular.element('#password1')[0].value;
  angular.element('#password2')[0].value = password;
  angular.element('#registration')[0].submit();
});
