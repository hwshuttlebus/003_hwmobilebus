'use strict';

angular.module('hwmobilebusApp')
    .controller('MapeditCtrl', function ($scope, $filter, $uibModal, BusinfoService, MapService) {
    
    /* location for libing Road campus */
    var longitude = 121.620443;
    var latitude = 31.201002;

    /* default direction to company */
    $scope.isDirToCompany = true;

    /* store all bus info */
    var businfo = BusinfoService.getbusinfo({id: 8}, function () {
       /* define campus */
      $scope.campus = [{Name: "李冰路", ID: 1},{Name: "环科路",ID: 2}];
      $scope.businfo = businfo;
      $scope.oldbusinfo = angular.copy($scope.businfo);
      for (var i=0; i<$scope.campus.length; i++) {
        if ($scope.campus[i].Name == $scope.businfo.campus) {
          $scope.selectedcampus = $scope.campus[i];
        }
      }
    });

    /* get all station info */
    var stationinfo = BusinfoService.getstationinfo({id: '8'}, function () {
      var templocal;
      var countup = 0;
      var countdown = 0;  
      for (var i=0; i<stationinfo.length; i++) {
        if (true == stationinfo[i].dirtocompany) {
          /* transfer date string to object */
          templocal = stationinfo[i];
          templocal.datetime = new Date("2000-01-01T"+stationinfo[i].time+":00");
          templocal.icon = "/static/images/"+String.fromCharCode(65+countup)+".png";
          countup++;
          $scope.tocompanystations.push(templocal);

          var parsedDate = $filter('date')(templocal.datetime, 'HH:mm');
        } else {
          /* transfer date string to object */
          templocal = stationinfo[i];
          templocal.datetime = new Date("2000-01-01T"+stationinfo[i].time+":00");
          templocal.icon = "/static/images/"+String.fromCharCode(65+countdown)+".png";
          countdown++;
          $scope.tohomestations.push(templocal);
        }
      }

      /* backup */
      $scope.oldtocompstation = angular.copy($scope.tocompanystations);
      $scope.oldtohomestation = angular.copy($scope.tohomestations);
    });

    
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

    $scope.loadmapedit = function (map) {
        var inputstations;
        $scope.map = map;
        if (true == $scope.isDirToCompany) {
            inputstations = $scope.tocompanystations;
        } else {
            inputstations = $scope.tohomestations;
        }
        MapService.loadmapedit($scope.map, inputstations);
    };

    $scope.tocompanystations = [];
    $scope.tohomestations = [];
    $scope.selected = 0;
    $scope.newmarker = {
      marker: null,
      stationid: 0,
    };
    $scope.tooltipctrl = {
      mapeditenablett: false
    };
    $scope.editctrl = {
      submit: false,
      submit2: false,
      cancel: false,
      cancel2: false,
      mapeditenable: false,  /* record whether map edit is enabled */
      addnewdisable: false
    };


    $scope.sortStation = function (stations) {
      var temp, datetime1, datetime2;
      for (var i=0;i<stations.length-1;i++) {
        for (var j=i+1; j<stations.length; j++) {
          if (stations[i].datetime > stations[j].datetime) {
            temp = stations[i];
            stations[i] = stations[j];
            stations[j] = temp;
          }
        }
      }
      /* icon */
      for (var i=0; i<stations.length; i++) {
        stations[i].icon = "/static/images/"+String.fromCharCode(65+i)+".png";
        /* for newly added */
        if (stations[i].id == 0xFF) {
          stations[i].id = 0xFE; /* marked as modified */
          stations[i].lat =  $scope.newmarker.marker.getPosition().lng;
          stations[i].lon = $scope.newmarker.marker.getPosition().lat;
        }
      }
    };

    $scope.buschange = function () {
      $scope.editctrl.submit=true;
      $scope.editctrl.cancel=true;
    };

    $scope.stationchange = function () {
      $scope.editctrl.submit2=true;
      $scope.editctrl.cancel2=true;
    };

    
    $scope.editmapenable = function (id) {
      $scope.editctrl.mapeditenable = true;
      $scope.tooltipctrl.mapeditenablett = true;
      /* create a draggable marker on center of current map */
      var mapCenter = $scope.map.getCenter();
      var point = new BMap.Point(mapCenter.lng,mapCenter.lat);
      $scope.newmarker.marker = new BMap.Marker(point);
      $scope.map.addOverlay($scope.newmarker.marker);
      $scope.newmarker.marker.setAnimation(BMAP_ANIMATION_DROP);
      $scope.newmarker.marker.enableDragging();
      /* record which station */
      $scope.newmarker.stationid = id;
    };

    $scope.editmapsubmit = function () {
      $scope.editctrl.mapeditenable = false;

      /* update new location */
      if ($scope.isDirToCompany) {
        var newstations = $scope.tocompanystations;
      } else {
        var newstations = $scope.tohomestations;
      }

      if (true == $scope.editctrl.addnewdisable) {
        /* during add new procedure sort by time */
        $scope.sortStation(newstations);
      } else {
        /* not in add new procedure , find the modified one */
        for (var i=0; i<newstations.length; i++) {
          if (newstations[i].id == $scope.newmarker.stationid) {
            newstations[i].lat = $scope.newmarker.marker.getPosition().lng;
            newstations[i].lon = $scope.newmarker.marker.getPosition().lat;
            break;
          }
        }
      }
      
      /* reload map */
      $scope.map.removeOverlay($scope.newmarker.marker);
      $scope.refreshmap(newstations);
      
      $scope.editctrl.submit2=true;
      $scope.editctrl.cancel2=true;
      $scope.editctrl.addnewdisable = false;
    };

    $scope.editmapcancel = function () {
      $scope.editctrl.mapeditenable = false;
      $scope.editctrl.mapeditenablett = false;
      $scope.map.removeOverlay($scope.newmarker.marker);
    };

    $scope.addnewstation = function () {
      /* enable map edit */
      $scope.editmapenable(0xFE);
      /* disable add new button */
      $scope.editctrl.addnewdisable = true;
      /* edit new station info */
      if ($scope.isDirToCompany) {
        var newstations = $scope.tocompanystations;
      } else {
        var newstations = $scope.tohomestations;
      }

      var newstation = {
        id: 0xFF,
        bus_id: newstations[0].bus_id,
        campus: newstations[0].campus,
        description: "",
        dirtocompany: $scope.isDirToCompany,
        lat: $scope.newmarker.marker.getPosition().lng,
        lon: $scope.newmarker.marker.getPosition().lat,
        name: "",
        time: "7:00",
        datetime: new Date("2000-01-01T07:00")
      };
      newstations.push(newstation);
    };

    $scope.select = function(index) {
      $scope.selected = index;
    };

    var modalInstance = '';
    $scope.delconfirm = function (id) {
      modalInstance = $uibModal.open({
        animation: true,
        templateUrl: 'delstationModal.html',
        controller: 'modalOpenCtrl',
        scope: $scope,
        size: 'md',
        backdrop: 'static',
        resolve: {
          delid: id
          }
        });
     };

    $scope.submit = function () {

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