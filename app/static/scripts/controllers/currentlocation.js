'use strict';

/**
 * @ngdoc function
 * @name hwmobilebusApp.controller:CurrentlocationCtrl
 * @description
 * # CurrentlocationCtrl
 * Controller of the hwmobilebusApp
 */
angular.module('hwmobilebusApp')
  .controller('CurrentlocationCtrl', function ($scope, $http, $window, $location, BusinfoService, InterfService, MapService) {
    /* location for libing Road campus */
    var longitude = 121.620443;
    var latitude = 31.201002;
    var maptemp;
    /* state machine for load route */
    var RouteLoadFSM = {
      initstate: true,
      maploaded: false,
      stationget: false,
      routeloaded: false
    };
    
    
    var loadmapcomplete = function () {
      $scope.loadctrl.mapinfo = false;
      $scope.$apply();
    };

    var initbusstation = function () {
      /* init flag */
      $scope.loadctrl.businfo = true;
      $scope.loadctrl.stationinfo = true;
      $scope.loadctrl.mapinfo = true;
      /* store all bus info */
      BusinfoService.getbusinfo({id:$scope.busid}, function(businfo) {
        $scope.businfo = businfo;
        $scope.loadctrl.businfo = false;
      }, function (error) {
        console.log('error:'+error.status);
      });

      /* get all station info */
      BusinfoService.getstationinfo({id: $scope.busid}, function (inputstationinfo) {
        var templocal;
        var countup = 0;
        var countdown = 0;
        var stationinfo = [];

        stationinfo = inputstationinfo;
        stationinfo.push(InterfService.gencompstation(true, longitude, latitude));
        stationinfo.push(InterfService.gencompstation(false, longitude, latitude));

        for (var i=0; i<stationinfo.length; i++) {
          if (true == stationinfo[i].dirtocompany) {
            /* transfer date string to object */
            templocal = stationinfo[i];
            templocal.datetime = new Date("2018-01-01T"+stationinfo[i].time+":00");
            templocal.icon = "/static/images/"+String.fromCharCode(65+countup)+".png";
            templocal.char = String.fromCharCode(65+countup);
            countup++;
            $scope.tocompanystations.push(templocal);
          } else {
            /* transfer date string to object */
            templocal = stationinfo[i];
            templocal.datetime = new Date("2018-01-01T"+stationinfo[i].time+":00");
            templocal.icon = "/static/images/"+String.fromCharCode(65+countdown)+".png";
            templocal.char = String.fromCharCode(65+countdown);
            countdown++;
            $scope.tohomestations.push(templocal);
          }
        }

        /* render route if map ready */
        if (true == RouteLoadFSM.maploaded) {
          var inputstations;
          if (true == $scope.isDirToCompany) {
              inputstations = $scope.tocompanystations;
          } else {
              inputstations = $scope.tohomestations;
          }
          MapService.loadmap(maptemp, inputstations, loadmapcomplete);
          /* state change to route loaded */
          RouteLoadFSM.maploaded = false;
          RouteLoadFSM.routeloaded = true;
        } else if (true == RouteLoadFSM.initstate) {
          RouteLoadFSM.initstate = false;
          RouteLoadFSM.stationget = true;
        }

        $scope.loadctrl.stationinfo = false;
      }, function (error) {

      });
    };

    var updatestation = function () {
      if ($scope.isDirToCompany == true) {
        $scope.stations = $scope.tocompanystations;
      } else {
        $scope.stations = $scope.tohomestations;
      }
    };


    $scope.usedseat= "";
    $scope.tocompanystations = [];
    $scope.tohomestations = [];
    /* default direction to company */
    $scope.isDirToCompany = true;
    /* loading control */
    $scope.loadctrl = {
      businfo: false,
      stationinfo: false,
      mapinfo: false,
      submit: false
    };

    $scope.busid = InterfService.getbusid();
    initbusstation();

    $scope.reload = function () {
      $window.location.reload();
    };

    $scope.offlineOpts = {
      /* no network condition */
      retryInterval: 10000,
      txt: '当前设备未联网'
    };
    /* mapOptions */
    $scope.mapOptions = {
      centerAndZoom: {
        longitude: longitude,
        latitude: latitude,
        zoom: 15
      },
      enableKeyboard: true,
      disableDragging: false,
      enableScrollWheelZoom: true
    };

    $scope.loadmap = function (map) {
      var inputstations;
      if (true == $scope.isDirToCompany) {
          inputstations = $scope.tocompanystations;
      } else {
          inputstations = $scope.tohomestations;
      }
      /* state machine handle */
      if (true == RouteLoadFSM.stationget) {
        /* loadmap when station is get or in newly added bus procedure */
        MapService.loadmap(map, inputstations, loadmapcomplete);
        /* enter route loaded state */
        RouteLoadFSM.stationget = false;
        RouteLoadFSM.routeloaded = true;
        if (inputstations.length < 2) {
          $scope.loadctrl.mapinfo = false;
        }
      } else if (true == RouteLoadFSM.initstate) {
        maptemp = map;
        RouteLoadFSM.initstate = false;
        RouteLoadFSM.maploaded = true;
      }
    };

    $scope.$watchCollection("isDirToCompany", function() {
      updatestation();
    });

});
