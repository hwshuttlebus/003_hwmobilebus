'use strict';

/**
 * @ngdoc function
 * @name hwmobilebusApp.controller:CurrentlocationCtrl
 * @description
 * # CurrentlocationCtrl
 * Controller of the hwmobilebusApp
 */
angular.module('hwmobilebusApp')
  .controller('CurrentlocationCtrl', function ($scope, $window, $location, $interval, BusinfoService, InterfService, MapService) {
    /* location for libing Road campus */
    var longitude = 121.620443;
    var latitude = 31.201002;
    var currentidx = 0; /* current index in stations */
    var maptemp;
    var busmarker = null;
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

    /* function to be called when all data is get */
    var allinfoget = function () {
      /* update station as per direction */
      updatestation();
      /* update current html attribute */
      updateattr();
      /* state change to route loaded */
      RouteLoadFSM.maploaded = false;
      RouteLoadFSM.routeloaded = true;
    };

    var getbus = function (isinit) {
      BusinfoService.getbusinfo({id:$scope.busid}, function(businfo) {
        $scope.businfo = businfo;
        $scope.loadctrl.businfo = false;

        /* during periodic procedure, update location after get bus info */
        if (false == isinit) {
          /* update current html attribute */
          updateattr();
        }
      }, function (error) {
        console.log('error:'+error.status);
      });
    };

    var initbusstation = function () {
      /* init flag */
      $scope.loadctrl.businfo = true;
      $scope.loadctrl.stationinfo = true;
      $scope.loadctrl.mapinfo = true;
      /* store all bus info */
      getbus(true);

      /* get all station info */
      BusinfoService.getstationinfo({id: $scope.busid}, function (inputstationinfo) {
        var templocal;
        var countup = 0;
        var countdown = 0;
        var stationinfo = [];

        stationinfo = inputstationinfo;

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
          allinfoget();
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

    /* function to update specific attribute in html based on result of server */
    var updateattr = function () {
      var distance, lefttime;
      /* recalculate lefttime in Integer:  the smallest integer greater than or equal to a number. */
      lefttime = Math.ceil($scope.businfo.lefttime);
      if (0 ==  lefttime) {
        lefttime = 1;
      }
      /* update html attribute */
      for (var i=0; i<$scope.stations.length; i++) {
        if (0xFF == $scope.businfo.currindx) {
          $scope.stations[i].attr3 = "greyout";
          $scope.stations[i].attr2 = "greyout";
          $scope.stations[i].attr1 = "greyout";
          $scope.stations[i].locinfo = "无班车位置数据"
          MapService.removemarker(false, busmarker);
          busmarker = null;
        } else {
          if (i <= $scope.businfo.currindx) {
            $scope.stations[i].attr3 = "greyout";
            $scope.stations[i].attr2 = "greyout";
            $scope.stations[i].attr1 = "greyout";
            $scope.stations[i].locinfo = "已到站"
            busmarker = null;
          } else if ((i>$scope.businfo.currindx) && (i<($scope.stations.length-1))){
            $scope.stations[i].attr3 = "";
            $scope.stations[i].attr2 = "";
            $scope.stations[i].attr1 = "normal";
            if (i != ($scope.businfo.currindx+1)) {
              $scope.stations[i].attr1 = "";
              distance = MapService.getDist(false, $scope.stations[$scope.businfo.currindx+1], $scope.stations[i+1]);
              lefttime = Math.ceil(lefttime+distance*1.5/15/60);
            }
            $scope.stations[i].locinfo = "约"+lefttime+"分钟";
          } else/* i == $scope.stations.length-1 */ {
            $scope.stations[i].attr3 = "redhighlight";
            $scope.stations[i].attr2 = "";
            $scope.stations[i].attr1 = "";
            if ($scope.businfo.currindx == $scope.stations.length) {
              $scope.stations[i].locinfo = "已到站"
              MapService.removemarker(false, busmarker);
            } else if ($scope.businfo.currindx == ($scope.stations.length-1)){
              $scope.stations[i].locinfo = "约"+lefttime+"分钟";
              /* update map bus marker */
              busmarker =  MapService.updatemarker(false, busmarker, $scope.businfo.lon, $scope.businfo.lat);
            } else {
              distance = MapService.getDist(false, $scope.stations[$scope.businfo.currindx+1], $scope.stations[i]);
              lefttime = Math.ceil(lefttime+distance*1.5/15/60);
              $scope.stations[i].locinfo = "约"+lefttime+"分钟";
              /* update map bus marker */
              busmarker =  MapService.updatemarker(false, busmarker, $scope.businfo.lon, $scope.businfo.lat);
            }
          } 
        }
      }
    };

    var updateloc = function () {
      getbus(false);
    };

    /* update location for every 3 seconds */
    var myInterval = $interval(updateloc, 3000);

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
        allinfoget();
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
      /* only refresh when route is loaded */
      if (true == RouteLoadFSM.routeloaded) {
        $scope.loadctrl.mapinfo = true;
        MapService.refreshmap(false, $scope.stations, loadmapcomplete);
        if ($scope.stations.length < 2) {
          $scope.loadctrl.mapinfo = false;
        }
      }
    });

    /* stop periodical get after route change */
    $scope.$on("$destroy", function() {
      $interval.cancel(myInterval);
    });

    /* click on station handler */
    $scope.clickupdate = function () {
      /* update bus location from server */
      $scope.loadctrl.businfo = true;
      updateloc();
    };
});
