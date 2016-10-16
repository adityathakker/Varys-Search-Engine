export function routerConfig ($stateProvider, $urlRouterProvider) {
  'ngInject';
  $stateProvider
    .state('home', {
      url: '/',
      templateUrl: 'app/main/main.html',
      controller: 'SearchController',
      controllerAs: 'searchController'
    });

  $urlRouterProvider.otherwise('/');
}
