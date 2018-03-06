'use strict';

/**
 * @ngdoc function
 * @name hwmobilebusApp.controller:BaidumapCtrl
 * @description
 * # BaidumapCtrl
 * Controller of the hwmobilebusApp
 */
angular.module('hwmobilebusApp')
  .controller('BaidumapCtrl', function ($scope, $location, $interval, BusinfoService, MapService) {

    
    var tocompanystations = [];
    var tohomestations = [];
    var markerarray = [];

    /* default direction to company */
    $scope.isDirToCompany = true;

    /* collection all bus stop markers */
    var stationinfo = BusinfoService.getstationinfo({id: '15'}, function () {
      for (var loopi=0; loopi<stationinfo.length; loopi++) {
        if (true == stationinfo[loopi].dirtocompany) {
          tocompanystations.push(stationinfo[loopi]);
        } else {
          tohomestations.push(stationinfo[loopi]);
        }
      }
    });
    
    
    
   

    /* refresh map */
    $scope.refreshmap = function (inputstations) {
      /* reset loading flag */
      $scope.loading = true;
      /* delete all markers */
      $scope.deleteallMarkers();
      /* delete all search route */
      $scope.removedrivingroute();
      /* reset */
      //$scope.map.reset();
      /* re-render route and markers */
      $scope.loadroute($scope.map, inputstations);
      /* re-render bus position */
    }

    /* delete all Markers */
    $scope.deleteallMarkers = function () {
      for (var loopi=0; loopi<markerarray.length; loopi++) {
        $scope.map.removeOverlay(markerarray[loopi]);
      }
    };

    /* remove route */
    $scope.removedrivingroute = function () {
      $scope.driving.clearResults();
    };

    /* create route */
    $scope.loadroute = function (map, inputstations) {
      var pointArray = new Array();
      var stations = inputstations;

      for (var loopi=0; loopi<stations.length;loopi++){
        pointArray[loopi] = new BMap.Point(stations[loopi].lat,stations[loopi].lon);
      }

      /* save internal stations(except start/end station) */
      var parray2 = [];
      for (loopi=1; loopi<pointArray.length-1; loopi++) {
        parray2.push(pointArray[loopi]);
      }

      var driving = new BMap.DrivingRoute(map, {renderOptions:{map: map},autoViewport: true, 
        policy: BMAP_TRANSIT_POLICY_LEAST_TIME,
        onMarkersSet: function (res) {
          //console.log(res)     
          /* replace marker for all the stations */
          for (var loopj=0; loopj<pointArray.length; loopj++) {
            
            var iconpath = "/static/images/"+String.fromCharCode(65+loopj)+'.png';
            var IconEntity = new BMap.Icon(iconpath, new BMap.Size(23, 36));
            var wayPointIconHtml='<div style="position: absolute; margin: 0px; padding: 0px; width: 36px; height: 40px; overflow: hidden;"><img src='+iconpath+' style="display: none; border:none;margin-left:-11px; margin-top:-35px; "></div>'
            var myPoint = new BMap.Marker(pointArray[loopj], {icon: IconEntity});
            
            /* record all markers */
            markerarray.push(myPoint);

            if (loopj===0 || loopj===pointArray.length-1) {
              /* for start and end station */
              map.removeOverlay(res[loopj].marker);
              map.addOverlay(myPoint);
            } else {
              /* for all the internal stations */
              res[loopj].Nm.Yc.innerHTML=wayPointIconHtml;
              map.addOverlay(myPoint);
            }
            myPoint.addEventListener("click", function () {
              //console.log(pointArray);
            });
          }
          $scope.loading = false;
        }
        
      });
      
      /* record driving result */
      $scope.driving = driving;
      /* record loading result */
      $scope.loading = false;

      /* 获取marker信息 */
      function showinfo(e) {
        var p = e.target;
        alert("marker: " + p.getPosition().lng + "," + p.getPosition.lat);
      }
      driving.search(pointArray[0], pointArray[pointArray.length-1], {waypoints: parray2});
    };

    $scope.tocomptabselect = function () {
      $scope.isDirToCompany = true;
      /*
      if (true == $scope.firstload) {
        $scope.firstload = false;
        refreshmap();
      }
      */
    };

    $scope.tohometabselect = function () {
      $scope.isDirToCompany = false;
      /*
      refreshmap();
      */
    };

  });
