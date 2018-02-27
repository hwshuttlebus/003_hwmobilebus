'use strict';

angular.module('hwmobilebusApp')
    .controller('MapeditCtrl', function ($scope, $filter, $uibModal, $window, BusinfoService, MapService) {
    
    var busid = 15;

    /* location for libing Road campus */
    var longitude = 121.620443;
    var latitude = 31.201002;
    /* state machine for load route */
    var RouteLoadFSM = {
      initstate: true,
      maploaded: false,
      stationget: false,
      routeloaded: false
    };
    var maptemp;
    /* default direction to company */
    $scope.isDirToCompany = true;
    $scope.map = null;
    /* loading control */
    $scope.loadctrl = {
      businfo: true,
      stationinfo: true,
      mapinfo: true
    };


    /* store all bus info */
    BusinfoService.getbusinfo({id:busid}, function(businfo) {
      /* define campus */
      $scope.campus = [{Name: "李冰路", ID: 1},{Name: "环科路",ID: 2}];
      $scope.businfo = businfo;
      $scope.oldbusinfo = angular.copy($scope.businfo);
      for (var i=0; i<$scope.campus.length; i++) {
        if ($scope.campus[i].Name == $scope.businfo.campus) {
          $scope.selectedcampus = $scope.campus[i];
        }
      }
      $scope.loadctrl.businfo = false;
    }, function (error) {
      console.log('error:'+error.status);
    });


    /* get all station info */
    BusinfoService.getstationinfo({id: busid}, function (stationinfo) {
      var templocal;
      var countup = 0;
      var countdown = 0;  

      for (var i=0; i<stationinfo.length; i++) {
        if (true == stationinfo[i].dirtocompany) {
          /* transfer date string to object */
          templocal = stationinfo[i];
          templocal.datetime = new Date("2018-01-01T"+stationinfo[i].time+":00");
          templocal.icon = "/static/images/"+String.fromCharCode(65+countup)+".png";
          countup++;
          $scope.tocompanystations.push(templocal);
        } else {
          /* transfer date string to object */
          templocal = stationinfo[i];
          templocal.datetime = new Date("2018-01-01T"+stationinfo[i].time+":00");
          templocal.icon = "/static/images/"+String.fromCharCode(65+countdown)+".png";
          countdown++;
          $scope.tohomestations.push(templocal);
        }
      }

      /* backup */
      $scope.oldtocompstation = angular.copy($scope.tocompanystations);
      $scope.oldtohomestation = angular.copy($scope.tohomestations);

      /* render route if map ready */
      if (true == RouteLoadFSM.maploaded) {
        var inputstations;
        if (true == $scope.isDirToCompany) {
            inputstations = $scope.tocompanystations;
        } else {
            inputstations = $scope.tohomestations;
        }
        MapService.loadmapedit(maptemp, inputstations);
        /* state change to route loaded */
        RouteLoadFSM.maploaded = false;
        RouteLoadFSM.routeloaded = true;
        $scope.loadctrl.mapinfo = false;
      } else if (true == RouteLoadFSM.initstate) {
        RouteLoadFSM.initstate = false;
        RouteLoadFSM.stationget = true;
      }

      $scope.loadctrl.stationinfo = false;
    }, function (error) {

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

        if (true == $scope.isDirToCompany) {
            inputstations = $scope.tocompanystations;
        } else {
            inputstations = $scope.tohomestations;
        }

        /* state machine handle */
        if (true == RouteLoadFSM.stationget) {
          MapService.loadmapedit(map, inputstations);
          /* enter route loaded state */
          RouteLoadFSM.stationget = false;
          RouteLoadFSM.routeloaded = true;
        } else if (true == RouteLoadFSM.initstate) {
          maptemp = map;
          RouteLoadFSM.initstate = false;
          RouteLoadFSM.maploaded = true;
        }

        $scope.loadctrl.mapinfo = false;
    };

    $scope.tocompanystations = [];
    $scope.tohomestations = [];
    $scope.selected = 0;
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
      $scope.newmarker = MapService.createmarker(id);
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
      MapService.removemarker($scope.newmarker.marker);
      MapService.refreshmap(true, newstations);
      
      $scope.editctrl.submit2=true;
      $scope.editctrl.cancel2=true;
      $scope.editctrl.addnewdisable = false;
    };

    $scope.editmapcancel = function () {
      $scope.editctrl.mapeditenable = false;
      $scope.editctrl.mapeditenablett = false;
      MapService.removemarker($scope.newmarker.marker);
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
        datetime: new Date("2018-01-01T07:00")
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
      var busStationinfo = new BusinfoService();
      busStationinfo.bus_name = $scope.businfo.name;
      busStationinfo.bus_cz_name  = $scope.businfo.cz_name;
      busStationinfo.bus_cz_phone = $scope.businfo.cz_phone;
      busStationinfo.bus_sj_name = $scope.businfo.sj_name;
      busStationinfo.bus_sj_phone = $scope.businfo.sj_phone;
      busStationinfo.bus_seat_num = $scope.businfo.seat_num;
      busStationinfo.bus_equip_id = $scope.businfo.equip_id;
      busStationinfo.bus_color = $scope.businfo.color;
      busStationinfo.bus_buslicense = $scope.businfo.buslicense;
      busStationinfo.bus_campus = $scope.businfo.campus;
      /* ensure do not post company itself into database */
      busStationinfo.station_tocompany = [];
      busStationinfo.station_tohome = [];
      for (var i=0; i<$scope.tocompanystations.length-1; i++) {
        /* transfer datetime to string */
        var parsedDate = $filter('date')($scope.tocompanystations[i].datetime, 'HH:mm');
        $scope.tocompanystations[i].time = parsedDate;
        busStationinfo.station_tocompany.push($scope.tocompanystations[i]);
      }
      for (var j=1; j<$scope.tohomestations.length; j++) {
        /* transfer datetime to string */
        var parsedDate = $filter('date')($scope.tohomestations[j].datetime, 'HH:mm');
        $scope.tohomestations[j].time = parsedDate;
        busStationinfo.station_tohome.push($scope.tohomestations[j]);
      }

      //console.log(JSON.stringify(busStationinfo,null, 4));

      busStationinfo.$updatestation({id: busid}, function (res) {
        console.log(res);
        $window.location.reload();
      }, function (error) {
        console.log(error.status);
      });
    };

    $scope.tocomptabselect = function () {
        $scope.isDirToCompany = true;
        /* only refresh when route is loaded */
        if (true == RouteLoadFSM.routeloaded) {
          MapService.refreshmap(true, $scope.tocompanystations);
        }
      };
  
    $scope.tohometabselect = function () {
        $scope.isDirToCompany = false;
        /* only refresh when route is loaded */
        if (true == RouteLoadFSM.routeloaded) {
          MapService.refreshmap(true, $scope.tohomestations);
        }
      };
});