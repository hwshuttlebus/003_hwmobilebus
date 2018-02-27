'use strict';

/**
 * @ngdoc function
 * @name hwmobilebusApp.controller:CurrentlocationCtrl
 * @description
 * # CurrentlocationCtrl
 * Controller of the hwmobilebusApp
 */
angular.module('hwmobilebusApp')
  .controller('CurrentlocationCtrl', function ($scope, $http, $window, BusinfoService) {
    $scope.tocompanystations = [];
    $scope.tohomestations = [];

    var businfo = BusinfoService.getbusinfo({id: '15'}, function () {
      $scope.captain= businfo.cz_name;
      $scope.driver= businfo.sj_name;
      $scope.captainphone= businfo.cz_phone;
      $scope.driverphone= businfo.sj_phone;
      $scope.totalseat= ''+businfo.seat_num;/* neet to convert to string type */
      $scope.buslicense= businfo.buslicense;
      $scope.buscolor= businfo.color;
    });

    var stationinfo = BusinfoService.getstationinfo({id: '15'}, function () {
      for (var loopi=0; loopi<stationinfo.length; loopi++) {
        if (true == stationinfo[loopi].dirtocompany) {
          $scope.tocompanystations.push(stationinfo[loopi]);
        } else {
          $scope.tohomestations.push(stationinfo[loopi]);
          console.log($scope.tohomestations)
        }
      }
    });
    
    $scope.usedseat= "";

    $scope.reload = function () {
      //$route.reload();
      $window.location.reload();
    };
  });
