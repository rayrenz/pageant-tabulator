(function () {
'use strict';
angular.module('myApp')
    .controller('LoginController', LoginController);

LoginController.$inject = ['AuthService', 'auth', '$scope', '$state'];

function LoginController (AuthService, auth, $scope, $state) {
  var ln = this;
  $scope.auth = auth.data;
  ln.login = function () {
    if ($scope.loginForm.$valid) {
      AuthService.login(ln.username, ln.password).then(function (resp) {
        if (resp.data.authenticated && resp.data.role === 'j') {
          $state.transitionTo('root.scoresheet', {}, {reload:true});
        } else if (resp.data.authenticated && resp.data.role === 't') {
          $state.transitionTo('root.tabulation', {}, {reload:true});
        }
      })
    }
  }
}
})();