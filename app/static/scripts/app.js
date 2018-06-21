'use strict';

/**
 * @ngdoc overview
 * @name hwmobilebusApp
 * @description
 * # hwmobilebusApp
 *
 * Main module of the application.
 */
var ngBaiduMap = window.ngBaiduMap;

angular
  .module('hwmobilebusApp', [
    ngBaiduMap,
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'ui.bootstrap'
  ])
  .config(['mapScriptServiceProvider', function(provider) {
    provider.setKey('r0I4Q4kag6t0ZcomSGU8C5zPUDHcWoOP')
  }])
  .config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
  })
  .config(function ($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix('');
    $routeProvider
    .when('/home', {
      templateUrl: 'static/partials/home.html',
      controller: 'MainCtrl'
    })
    .when('/busList/currentlocation', {
      templateUrl: 'static/partials/currentlocation.html',
      controller: 'CurrentlocationCtrl'
    })
    .when('/busList', {
      templateUrl: 'static/partials/busList.html',
      controller: 'BuslistCtrl'
    })
    .when('/busListEdit/busEditmain', {
      templateUrl: 'static/partials/busEditmain.html',
      controller: 'MapeditCtrl'
    })
    .when('/busListEdit', {
      templateUrl: 'static/partials/busListEdit.html',
      controller: 'BuseditCtrl'
    })
    .when('/dataanalysis',{
      templateUrl: 'static/partials/dataAnalysis.html',
      controller: 'busAnalysisCtrl'
    })
    .when('/stationAnalysis',{
      templateUrl: 'static/partials/stationAnalysis.html',
      controller: 'stationAnalysisCtrl'
    })
    .when('/suggestion', {
      templateUrl: 'static/partials/suggestion.html',
      controller: 'SuggestionCtrl'
    })
    .when('/mybus', {
      templateUrl: 'static/partials/mybus.html',
      controller: 'MybusCtrl'
    })
    .when('/employmanage', {
      templateUrl: 'static/partials/employmanage.html',
      controller: 'EmploymanageCtrl'
    })
    .when('/broadcastmsg', {
      templateUrl: 'static/partials/broadcastmsg.html',
      controller: 'BroadcastCtrl'
    })
    .otherwise({
      redirectTo: '/home'
    });
    
  });
