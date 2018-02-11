'use strict';

angular.element('#password-change').submit(function(e) {
  e.preventDefault();
  const password = angular.element('#new_password1')[0].value;
  angular.element('#new_password2').value = password;
  angular.element('#password-change')[0].submit();
});
