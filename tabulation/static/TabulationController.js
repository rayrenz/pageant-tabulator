(function () {
'use strict';
angular.module('myApp')
    .controller('TabulationController', TabulationController);

TabulationController.$inject = ['$stateParams', 'auth', '$scope', '$state', 'candidates', 'categories', '$transitions', 'ScoreService'];

function TabulationController ($stateParams, auth, $scope, $state, candidates, categories, $transitions, ScoreService) {
  var tab = this;
  $scope.auth = auth.data;
  tab.candidates = candidates.data;
  tab.categories = categories.data;
  tab.category = $stateParams.category;
  tab.judgeScores = [];

  (function () {
    ScoreService.getJudgeScores(tab.category).then(function (resp) {
      tab.judgeScores = resp.data;
      updateAverages();
    })
  })();

  tab.getScore = function (id, username) {
    for(var i = 0; i < tab.judgeScores.length; i++) {
      if (tab.judgeScores[i].username === username) {
        for (var x = 0; x < tab.judgeScores[i].scores.length; x ++) {
          if (tab.judgeScores[i].scores[x].candidate === id) {
            return tab.judgeScores[i].scores[x].points;
          }
        }
        break;
      }
    }
  };

  function updateRanks () {
    console.log(tab.candidates);
    var averages = [];
    for (var c = 0; c < tab.candidates.length; c++) {
      var candidate = tab.candidates[c];
      candidate.rank = "";
      if (typeof candidate.average === 'number') {
        averages.push([candidate.id, candidate.average]);
      }
    }
    console.log(averages);
    averages.sort(function (a, b) {
      return b[1] - a[1];
    });
    console.log(averages);
    var prev;
    var x= 1;
    for (var i = 0; i < averages.length; i++) {
      var average = averages[i];
      for (var c = 0; c < tab.candidates.length; c++) {
        var candidate = tab.candidates[c];
        if (candidate.id === average[0]) {
          if (!prev) prev = average[1];
          candidate['rank'] = (average[1] !== prev) ? ++x : x;
          prev = average[1];
        }
      }
    }
    console.log(tab.candidates);
  }

  function sum (total, num) {
    return total + num;
  }

  function updateAverages () {
    for (var c = 0; c < tab.candidates.length; c++) {
      var candidate = tab.candidates[c];
      candidate['average'] = '';
      var scores = [];
      for (var i = 0; i < tab.judgeScores.length; i++) {
        var judge = tab.judgeScores[i];
        for (var x = 0; x < judge.scores.length; x++) {
          var score = judge.scores[x];
          if (score.candidate === candidate.id) {
            scores.push(score.points);
          }
        }
      }
      if (scores.length > 0) {
        candidate['average'] = (scores.reduce(sum) / scores.length).toFixed(2);
      }
    }
    updateRanks();
  }

  $transitions.onSuccess(function (transition) {
    tab.category = transition.params().category;
  });
}
})();