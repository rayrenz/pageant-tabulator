(function () {
angular.module('myApp')
    .service('ScoreService', ScoreService);

ScoreService.$inject = ['$http', '$location', '$timeout', '$rootScope', '$q'];

function ScoreService ($http, $location, $timeout, $rootScope, $q) {
  var service = this;

  service.getScores = function (category) {
    var d = $q.defer();
    if (category === undefined) d.reject();
    $http.get('/scores/' + category)
        .then(function (resp) {
          d.resolve(resp);
        });
    return d.promise;
  };

  service.getCandidates = function () {
    var d = $q.defer();
    $http.get('/candidates')
        .then(function (resp) {
          d.resolve(resp);
        });
    return d.promise;
  };

  service.getCategories = function () {
    var d = $q.defer();
    $http.get('/categories')
      .then(function (resp) {
        d.resolve(resp);
      });
    return d.promise;
  };

  service.submitFinal = function (scores) {
    return $http({
      url: '/final',
      method: 'POST',
      data: JSON.stringify(scores)
    });
  };
  
  service.submit = function (newScores, category) {
    var d = $q.defer();
    $http({
      url: '/scores/' + category,
      data: JSON.stringify(newScores),
      method: 'POST'
    }).then(function (resp) {
      d.resolve(resp);
    });
    return d.promise;
  };

  service.getJudgeScores = function (category) {
    var d = $q.defer();
    if (!category) d.reject();
    $http.get('/judges/' + category)
        .then(function (resp) {
          d.resolve(resp);
        });
    return d.promise;
  };

  service.getFinalScores = function () {
    console.log('getfinalscores');
    return $http.get('/final');
  }
}
})();