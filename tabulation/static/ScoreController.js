(function () {
'use strict';
angular.module('myApp')
    .controller('ScoreController', ScoreController);

ScoreController.$inject = ['ScoreService', 'candidates', 'categories', '$transitions', '$stateParams', 'auth', '$state', '$scope'];

function ScoreController (ScoreService, candidates, categories, $transitions, $stateParams, auth, $state, $scope) {
  // use stateparams to get route params on page load
  var sc = this;
  $scope.auth = auth.data;
  sc.categories = categories.data;
  sc.candidates = candidates.data;
  sc.category = $stateParams.category;
  sc.scores = {};
  sc.ranks = {};
  sc.judges = [];
  sc.finalScores = {};
  
  function updateRanking () {
    sc.ranks = {};
    var scores = Object.keys(sc.scores[sc.category]).map(function (key){
      return [key, sc.scores[sc.category][key]];
    });
    scores.sort(function (a, b) {
      return b[1] - a[1];
    });
    var x = 1;
    var prev;
    for (var i = 0; i < scores.length; i++) {
      if (!prev) prev = scores[i][1];
      sc.ranks[scores[i][0]] = (scores[i][1] !== prev) ? ++x : x;
      prev = scores[i][1];
    }
  }

  function updateScores (scores) {
    if (!sc.scores.hasOwnProperty(sc.category)) sc.scores[sc.category] = {};
    for (var i=0; i < scores.length; i++) {
      var s = scores[i];
      sc.scores[sc.category][s.candidate] = s.points;
    }
    updateRanking();
  }

  function updateFinalScores (scores) {
    for (var i = 0; i < sc.candidates.length; i++) {
      sc.finalScores[sc.candidates[i].id] = undefined;
    }
    for (var i = 0; i < scores.length; i++) {
      var s = scores[i];
      sc.finalScores[s.candidate] = s.rank;
    }
    console.log(sc.finalScores);
  }

  function getScores() {
    sc.scores = {};
    if ($state.current.name === 'scoresheet' || sc.category === 'final_interview') return;
    ScoreService.getScores(sc.category)
        .then(function (resp) {
          updateScores(resp.data);
        });
  }

  (function () {
    console.log(sc.category);
    if (sc.category && sc.category !== 'final_interview') {
      getScores();
    } else if (sc.category === 'final_interview') {
      ScoreService.getFinalScores().then(function (resp) {
        updateFinalScores(resp.data);
      });
    }
  })();

  $transitions.onSuccess({}, function (transition) {
    sc.category = transition.params().category;
    if (sc.category && sc.category !== 'final_interview') {
      getScores();
    } else if (sc.category === 'final_interview') {
      ScoreService.getFinalScores().then(function (resp) {
        updateFinalScores(resp.data);
      });
    }
  });
  
  sc.submitFinal = function () {

  };
  
  sc.checkScore = function (candidate) {
    if (sc.scores[sc.category][candidate]) {
      updateRanking();
    }
  };

  sc.submit = function () {
    if ($('.ng-invalid').length > 0) {
      showAlert('Invalid input!', 'error');
    } else if (sc.category !== 'final_interview') {
      ScoreService.submit(sc.scores[sc.category], sc.category).then(function (resp) {
        getScores();
        showAlert(resp.data.message, resp.data.type);
      });
    } else if (sc.category === 'final_interview') {
      ScoreService.submitFinal(sc.finalScores).then(function (resp) {
        ScoreService.getFinalScores().then(function (resp) {
          updateFinalScores(resp.data);
        });
        showAlert(resp.data.message, resp.data.type);
      })
    }
  };
}
})();