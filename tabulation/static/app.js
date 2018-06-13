(function () {
'use strict';
angular.module('myApp', ['ui.router'])
    .config(function ($httpProvider) {
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    })
    .config(RoutesConfig)
    .filter('rank', RankFilter)
    .run(function ($state) {
      $state.defaultErrorHandler(function (t) {
        console.log(t.message)
      });
    });

    RankFilter.$inject = ['$sce'];
    function RankFilter ($sce) {
      return function (input) {
        if (!input) return;
        switch (input) {
          case 1:
            return $sce.trustAsHtml('<span class="first">1st</span>');
          case 2:
            return $sce.trustAsHtml('<span class="second">2nd</span>');
          case 3:
            return $sce.trustAsHtml('<span class="third">3rd</span>');
          default:
            return $sce.trustAsHtml('<span class="others">'+ input + 'th</span>');
        }
      }
    }

    RoutesConfig.$inject = ['$stateProvider', '$urlRouterProvider'];

    function RoutesConfig ($stateProvider, $urlRouterProvider) {
      $stateProvider
          .state('root', {
            url: '',
            abstract: true, //abstract state cannot be activated
            resolve: {
              $state: '$state',
              auth: ['AuthService', '$q', '$state', '$stateParams', function (AuthService, $q, $state, $stateParams) {
                return AuthService.init();
              }]
            }
          })
          .state('root.login', {
            url: '/login',
            templateUrl: '/template/login.html',
            controller: 'LoginController as ln',
            resolve: {
              auth: function (auth, $state) {
                if (auth.data.authenticated && auth.data.role === 'j') {
                  $state.go('root.scoresheet');
                } else if (auth.data.authenticated && auth.data.role === 't') {
                  $state.go('root.tabulation')
                } else {
                  return auth;
                }
              }
            }
          })
          .state('root.scoresheet', {
            url: '/scoresheet',
            controller: 'ScoreController as sc',
            templateUrl: '/template/scoresheet.html',
            resolve: {
              ScoreService: 'ScoreService',
              auth: function (auth, $state) {
                if (!auth.data.authenticated) {
                  $state.transitionTo('root.login', {}, {reload: true});
                } else if (auth.data.role === 't') {
                  $state.transitionTo('root.tabulation', {}, {reload: true});
                } else {
                  return auth;
                }
              },
              candidates: function (ScoreService) {
                return ScoreService.getCandidates();
              },
              categories: function (ScoreService) {
                return ScoreService.getCategories();
              }
            }
          })
          .state('root.scoresheet.category', {
            url: '/{category}',
            controller: 'ScoreController as sc'
          })
          .state('root.tabulation', {
            url: '/tabulation',
            templateUrl: '/template/tabulation.html',
            controller: 'TabulationController as tab',
            resolve: {
              auth: function (auth, $state) {
                if (!auth.data.authenticated) {
                  $state.transitionTo('root.login', {}, {reload: true});
                } else if (auth.data.role === 'j') {
                  $state.transitionTo('root.scoresheet', {}, {reload: true});
                } else {
                  return auth;
                }
              },
              candidates: function (ScoreService) {
                return ScoreService.getCandidates();
              },
              categories: function (ScoreService) {
                return ScoreService.getCategories();
              }
            }
          })
          .state('root.tabulation.category', {
            url: '/{category}',
            templateUrl: '/template/tabulation-category.html',
            controller: 'TabulationController as tab'
          });
      $urlRouterProvider.otherwise('/login');
    }
})();

function getCookie(cname) {
  console.log(cname);
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function closeAlert () {
  $('#alert').fadeOut();
}
function showAlert (msg, type) {
  $('#alert').find('.message')[0].innerHTML = msg;
  if (type === 'error') {
    $('#alert').addClass('alert-danger').removeClass('alert-success');
  } else {
    $('#alert').addClass('alert-success').removeClass('alert-danger');
  }
  $('#alert').slideDown();
  window.scrollTo(0,0);
  setTimeout(function () {
    $('#alert').fadeOut();
  }, 3000);
}