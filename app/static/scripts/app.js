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
    })
    .when('/currentlocation', {
      templateUrl: 'static/partials/currentlocation.html',
      controller: 'CurrentlocationCtrl'
    })
    .when('/busList', {
      templateUrl: 'static/partials/busList.html',
      controller: 'BuslistCtrl'
    })
    .when('/busEditmain', {
      templateUrl: 'static/partials/busEditmain.html',
      controller: 'MapeditCtrl'
    })
    .when('/busListEdit', {
      templateUrl: 'static/partials/busListEdit.html',
      controller: 'BuseditCtrl'
    })
    .otherwise({
      redirectTo: '/home'
    });
    
  });
