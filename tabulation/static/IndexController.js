(function () {
'use strict';
angular.module('myApp')
    .controller('IndexController', IndexController);

IndexController.$inject = ['AuthService', '$scope', '$location', '$transitions', '$state', 'ScoreService', '$stateParams'];

function IndexController (AuthService, $scope, $location, $transitions, $state, ScoreService, $stateParams) {
  var index = this;

  index.logout = function () {
    AuthService.logout().finally(function () {
      index.authenticated = AuthService.getStatus('authenticated');
      index.user = AuthService.getStatus('user');
      $scope.$broadcast('reset');
      if (!index.authenticated) {
        location.href = '/#!/login';
        location.reload();
      }
    });
  };
}
})();