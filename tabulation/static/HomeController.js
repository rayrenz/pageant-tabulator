(function () {
'use strict';
angular.module('myApp')
    .controller('HomeController', HomeController);

HomeController.$inject = ['AuthService', '$location'];

function HomeController (AuthService, $location) {
  var vm = this;
}
})();