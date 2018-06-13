(function (jQuery) {
angular.module('myApp')
    .service('AuthService', AuthService);

AuthService.$inject = ['$http', '$location', '$timeout', '$rootScope', '$q', '$state'];

function AuthService ($http, $location, $timeout, $rootScope, $q, $state) {
  var service = this;
  var status = {
    authenticated: false,
    user: '',
    init: false,
    role: ''
  };
  var list = {
    judges: []
  };

  function broadCastStatus () {
    $rootScope.$broadcast('status');
  }

  $rootScope.$on('$routeChangeStart', function () {
    broadCastStatus();
  });

  service.getList = function (name) {
    return list[name];
  };

  service.init = function () {
    var d = $q.defer();
    $http.get('/auth')
        .then(function (resp) {
          d.resolve(resp);
        });
    return d.promise;
  };

  service.login = function (username, password) {
    var d = $q.defer();
    var data = {
      username: username,
      password: password
    };

    $http({
      url: '/login',
      method: 'POST',
      data: JSON.stringify(data)
    }).then(
        function (response) {
          d.resolve(response);
        }
    );
    return d.promise;
  };

  service.logout = function () {
    return $http
        .post('/logout')
        .then(function (response) {
          status.authenticated = response.data.authenticated;
          status.user = ''
        });
  };

  service.getStatus = function (name) {
    return status[name];
  };
}
})(jQuery);