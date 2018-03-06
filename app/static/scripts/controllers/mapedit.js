'use strict';

angular.module('hwmobilebusApp')
    .controller('MapeditCtrl', function ($scope, $filter, $uibModal, $window, $location, BusinfoService, MapService, InterfService) {
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
    /* define campus */
    $scope.campus = [{Name: "李冰路", ename:"libingroad", ID: 1, longitude: 121.620443, latitude: 31.201002},
                     {Name: "环科路", ename:"huankeroad", ID: 2, longitude: 121.611466, latitude: 31.182958}];

    
    var loadmapcomplete = function () {
      $scope.loadctrl.mapinfo = false;
      $scope.$apply();
    };

    var initnewbusstat = function () {
      /* init variable */
      $scope.businfo = {};
      /* set number field to integer 0 */
      $scope.businfo.number = 0;
      $scope.businfo.seat_num = 0;
      $scope.loadctrl.businfo = false;
      $scope.loadctrl.stationinfo = false;
      $scope.loadctrl.mapinfo = true;
      $scope.loadctrl.submit = false;
      $scope.selectedcampus = $scope.campus[0];
      $scope.tocompanystations.push(InterfService.gencompstation(true, $scope.selectedcampus.longitude, $scope.selectedcampus.latitude));
      $scope.tohomestations.push(InterfService.gencompstation(false, $scope.selectedcampus.longitude, $scope.selectedcampus.latitude));
    };

    var initbusstation = function () {
      /* init flag */
      $scope.loadctrl.businfo = true;
      $scope.loadctrl.stationinfo = true;
      $scope.loadctrl.mapinfo = true;
      $scope.loadctrl.submit = false;
      $scope.selectedcampus = $scope.campus[0];
      /* store all bus info */
      BusinfoService.getbusinfo({id:$scope.busid}, function(businfo) {
        $scope.businfo = businfo;
        $scope.oldbusinfo = angular.copy($scope.businfo);
        for (var i=0; i<$scope.campus.length; i++) {
          if ($scope.campus[i].ename == $scope.businfo.campus) {
            $scope.selectedcampus = $scope.campus[i];
          }
        }
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
        stationinfo.push(InterfService.gencompstation(true, $scope.selectedcampus.longitude, $scope.selectedcampus.latitude));
        stationinfo.push(InterfService.gencompstation(false, $scope.selectedcampus.longitude, $scope.selectedcampus.latitude));

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
          MapService.loadmapedit(maptemp, inputstations, loadmapcomplete);
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

    $scope.offlineOpts = {
      /* no network condition */
      retryInterval: 10000,
      txt: '当前设备未联网'
    };

    /* mapOptions */
    $scope.mapOptions = {
      centerAndZoom: {
          longitude: $scope.campus[0].longitude,
          latitude: $scope.campus[0].latitude,
          zoom: 15
      },
      enableKeyboard: true,
      disableDragging: false,
      enableScrollWheelZoom: true
    };
    /* loading control */
    $scope.loadctrl = {
      businfo: false,
      stationinfo: false,
      mapinfo: false,
      submit: false
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

    $scope.busid = InterfService.getbusid();
    if ("newaddbus" != $scope.busid) {
      initbusstation();
    } else {
      initnewbusstat();
    }

    var mapeditenable = function (id, selectid) {
      $scope.editctrl.mapeditenable = true;
      $scope.tooltipctrl.mapeditenablett = true;
      $scope.newmarker = MapService.createmarker(id, selectid);
    };
  
    $scope.loadmapedit = function (map) {
        var inputstations;
        if (true == $scope.isDirToCompany) {
            inputstations = $scope.tocompanystations;
        } else {
            inputstations = $scope.tohomestations;
        }
        /* state machine handle */
        if (true == RouteLoadFSM.stationget || "newaddbus" == $scope.busid) {
          /* loadmap when station is get or in newly added bus procedure */
          MapService.loadmapedit(map, inputstations, loadmapcomplete);
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

    $scope.buschange = function () {
      $scope.editctrl.submit=true;
      $scope.editctrl.cancel=true;
    };

    $scope.editmapenable = function (id, index) {
      mapeditenable(id, index);
    };

    $scope.editmapsubmit = function () {
      $scope.editctrl.mapeditenable = false;
      $scope.loadctrl.mapinfo = true;

      /* update new location */
      if ($scope.isDirToCompany) {
        var newstations = $scope.tocompanystations;
      } else {
        var newstations = $scope.tohomestations;
      }

      if (false == $scope.editctrl.addnewdisable) {
        /* not in add new procedure , find the modified one */
        for (var i=0; i<newstations.length; i++) {
          if ((newstations[i].id == $scope.newmarker.id) && (newstations[i].selectid == $scope.newmarker.selectid)) {
            newstations[i].lat = $scope.newmarker.marker.getPosition().lng;
            newstations[i].lon = $scope.newmarker.marker.getPosition().lat;
            break;
          }
        }
      }
      /* sort by time */
      InterfService.sortStation(newstations,$scope.newmarker.marker.getPosition().lng,$scope.newmarker.marker.getPosition().lat);
      /* reload map */
      MapService.removemarker($scope.newmarker.marker);
      MapService.refreshmap(true, newstations, loadmapcomplete);
      /* clear flag */
      if (newstations.length < 2) {
        $scope.loadctrl.mapinfo = false;
      }
      $scope.editctrl.submit=true;
      $scope.editctrl.cancel=true;
      $scope.editctrl.addnewdisable = false;
    };

    $scope.editmapcancel = function () {
      $scope.editctrl.mapeditenable = false;
      $scope.editctrl.mapeditenablett = false;
      MapService.removemarker($scope.newmarker.marker);
    };

    $scope.addnewstation = function () {
      /* edit new station info */
      if ($scope.isDirToCompany) {
        var newstations = $scope.tocompanystations;
      } else {
        var newstations = $scope.tohomestations;
      }
      /* enable map edit */
      mapeditenable("newstation", newstations.length);
      /* disable add new button */
      $scope.editctrl.addnewdisable = true;
      
      var newstation = {
        id: "newstation",
        selectid: newstations.length,
        bus_id: $scope.busid,
        campus: $scope.campus.ename,
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
    var genmodal = function (template, ctrl, size, resolve) {
      modalInstance = $uibModal.open({
          animation: true,
          templateUrl: template,
          controller: ctrl,
          scope: $scope,
          size: size,
          backdrop: 'static',
          resolve: resolve
        });
    };
    var geninfomodal = function (proc, title, content, template, ctrl, size) {
      var resolve = {
        items: function () {
          return {
            proc: proc,
            title: title,
            content: content
          };
        }
      };
      genmodal(template, ctrl, size, resolve);
    };

    $scope.delconfirm = function (id, datetime, selid) {
      var titlelocal = "注意！";
      var contentlocal = "确定要删除该站点吗？";
      var resolve = {
        items: function () {
          return {
            proc: 'stationDel',
            delid: id,
            deldatetime: datetime,
            selectid: selid, 
            dir: $scope.isDirToCompany,
            callbackfunc: loadmapcomplete,
            title: titlelocal,
            content: contentlocal
          };
        }
      }
      genmodal('infoModal.html', 'modalOpenCtrl', 'sm', resolve);
     };

    $scope.submit = function () {
      $scope.loadctrl.submit = true;
      var busStationinfo = new BusinfoService();
      busStationinfo.bus_name = $scope.businfo.name;
      busStationinfo.bus_number = $scope.businfo.number;
      busStationinfo.bus_cz_name  = $scope.businfo.cz_name;
      busStationinfo.bus_cz_phone = $scope.businfo.cz_phone;
      busStationinfo.bus_sj_name = $scope.businfo.sj_name;
      busStationinfo.bus_sj_phone = $scope.businfo.sj_phone;
      busStationinfo.bus_seat_num = $scope.businfo.seat_num;
      busStationinfo.bus_equip_id = $scope.businfo.equip_id;
      busStationinfo.bus_color = $scope.businfo.color;
      busStationinfo.bus_buslicense = $scope.businfo.buslicense;
      busStationinfo.bus_campus = $scope.selectedcampus.ename;
      /* ensure do not post company itself into database */
      busStationinfo.station_tocompany = [];
      busStationinfo.station_tohome = [];
      for (var i=0; i<$scope.tocompanystations.length-1; i++) {
        if ("company" != $scope.tocompanystations[i].id) {
          /* transfer datetime to string */
          var parsedDate = $filter('date')($scope.tocompanystations[i].datetime, 'HH:mm');
          $scope.tocompanystations[i].time = parsedDate;
          busStationinfo.station_tocompany.push($scope.tocompanystations[i]);
        }
      }
      for (var j=1; j<$scope.tohomestations.length; j++) {
        if ("company" != $scope.tohomestations[j].id) {
          /* transfer datetime to string */
          var parsedDate = $filter('date')($scope.tohomestations[j].datetime, 'HH:mm');
          $scope.tohomestations[j].time = parsedDate;
          busStationinfo.station_tohome.push($scope.tohomestations[j]);
        }
      }

      console.log(JSON.stringify(busStationinfo,null, 4));

      /* set loading flag */
      $scope.loadctrl.submit = true;

      if ("newaddbus" != $scope.busid) {
        busStationinfo.$updatestation({id: $scope.busid}, function (res) {
          $scope.loadctrl.submit = false;
          var result = JSON.stringify(res);
          if (result.indexOf('ERROR') != -1) {
            geninfomodal('busResp', '提交失败！', result, 'infoModal.html', 'modalOpenCtrl', 'sm');
          } else {
            geninfomodal('busResp', '提交成功！', '', 'infoModal.html', 'modalOpenCtrl', 'sm');
          }
        }, function (error) {
          geninfomodal('busResp', '提交失败！', error.status,'infoModal.html', 'modalOpenCtrl', 'sm');
        });
      } else {
        busStationinfo.$addbusstation(function (res) {
          $scope.loadctrl.submit = false;
          var result = JSON.stringify(res);
          if (result.indexOf('ERROR') != -1) {
            geninfomodal('busResp', '提交失败！', result, 'infoModal.html', 'modalOpenCtrl', 'sm');
          } else {
            geninfomodal('busResp', '提交成功！', '', 'infoModal.html', 'modalOpenCtrl', 'sm');
          }
        }, function (error) {
          geninfomodal('busResp', '提交失败！', error.status,'infoModal.html', 'modalOpenCtrl', 'sm');
        });
      }
    };

    $scope.cancelmodify = function () {
      geninfomodal('busCancel', '注意！', '请确认是否需要取消所有修改？', 'infoModal.html', 'modalOpenCtrl', 'sm');
    };

    $scope.tocomptabselect = function () {
        $scope.isDirToCompany = true;
        /* only refresh when route is loaded */
        if (true == RouteLoadFSM.routeloaded) {
          $scope.loadctrl.mapinfo = true;
          MapService.refreshmap(true, $scope.tocompanystations, loadmapcomplete);
          if ($scope.tocompanystations.length < 2) {
            $scope.loadctrl.mapinfo = false;
          }
        }
      };
  
    $scope.tohometabselect = function () {
        $scope.isDirToCompany = false;
        /* only refresh when route is loaded */
        if (true == RouteLoadFSM.routeloaded) {
          $scope.loadctrl.mapinfo = true;
          MapService.refreshmap(true, $scope.tohomestations, loadmapcomplete);
          if ($scope.tohomestations.length < 2) {
            $scope.loadctrl.mapinfo = false;
          }
        }
      };
});