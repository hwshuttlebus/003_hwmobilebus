'use strict';

angular.module('hwmobilebusApp')
    .controller('MybusCtrl', function ($scope, BusinfoService, InterfService, MapService) {
    /* location for libing Road campus */
    var longitude = 121.620443;
    var latitude = 31.201002;

    /* search location related variables */
    var marker = null;
    var recroutestate = {
        norecroute: true,
        inrecroute: false
    };
    var maptemp;
    var busid = 0;
    var allbuslocal={};
    var tocompanystations = [];
    var tohomestations = [];
    var getstate = {
        tocompget: false,
        tohomeget: false
    };


    /* init function */
    var initfunc = function () {
        /* get all bus info */
        $scope.loadctrl.businfo = true;
        $scope.loadctrl.stationinfo = true;
        BusinfoService.getallbus({}, function(allbus) {
            allbuslocal = allbus;
            /* get register bus info */
            BusinfoService.getregbus({}, function(regbus) {
                /* update register bus element in html */
                $scope.loadctrl.businfo = false;
                updatebus(regbus);
                if (regbus.tocompbus == "") {
                    var busidcomp = allbus[0].id;
                } else {
                    var busidcomp = regbus.tocompbus.id;
                }
                if (regbus.tohomebus == "") {
                    var busidhome = allbus[0].id;
                } else {
                    var busidhome = regbus.tohomebus.id;
                }
                /* get related to company station and update them in html */
                updatestation(busidcomp, busidhome, regbus);
            });
        });

    };

    var stationgetcallback = function (dir, regbus) {
        /* update options in html */
        if (true == dir) {
            $scope.options.tocompstations = [];
            $scope.regstation.tocomp = null;
            for (var j=0; j<tocompanystations.length; j++) {
                $scope.options.tocompstations.push(tocompanystations[j]);
                if (regbus != null) {
                    if (regbus.tocompstation.id == tocompanystations[j].id) {
                        $scope.regstation.tocomp = tocompanystations[j];
                    }
                }
            }
            if ($scope.regstation.tocomp == null) {
                $scope.regstation.tocomp = tocompanystations[0];
            }
        } else {
            $scope.options.tohomestations = [];
            $scope.regstation.tohome = null;
            for (var k=0; k<tohomestations.length; k++) {
                $scope.options.tohomestations.push(tohomestations[k]);
                if (regbus != null) {
                    if (regbus.tohomestation.id == tohomestations[k]) {
                        $scope.regstation.tohome = tohomestations[k];
                    }
                }
            }
            if ($scope.regstation.tohome == null) {
                $scope.regstation.tohome = tohomestations[0];
            }
        }
        $scope.loadctrl.stationinfo = false;
    };

    /* get station info based on bus info */
    var updatestation = function (busidcomp, busidhome, regbus, loadrouteneed) {
        $scope.loadctrl.stationinfo = true;
        tocompanystations = [];
        tohomestations = [];
        if (null != busidcomp) {
            BusinfoService.getstationinfo({id: busidcomp}, function (inputstationinfo) {
                var templocal;
                var countup = 0;
                var stationinfo = [];
    
                stationinfo = inputstationinfo;
                for (var i=0; i<stationinfo.length; i++) {
                    if (true == stationinfo[i].dirtocompany) {
                        /* transfer date string to object */
                        templocal = stationinfo[i];
                        templocal.icon = "/static/images/"+String.fromCharCode(65+countup)+".png";
                        countup++;
                        tocompanystations.push(templocal);
                    }
                }
                stationgetcallback(true, regbus);

                /* load route if need */
                if (true == loadrouteneed) {
                    $scope.loadctrl.mapinfo = true
                    MapService.loadmapedit(maptemp, tocompanystations, loadmapcomplete);
                }
            });   
        }

        if (null != busidhome) {
            BusinfoService.getstationinfo({id: busidhome}, function (inputstationinfo) {
                var templocal;
                var countdown = 0;
                var stationinfo = [];
    
                stationinfo = inputstationinfo;
                for (var i=0; i<stationinfo.length; i++) {
                    if (false == stationinfo[i].dirtocompany){
                        /* transfer date string to object */
                        templocal = stationinfo[i];
                        templocal.icon = "/static/images/"+String.fromCharCode(65+countdown)+".png";
                        countdown++;
                        tohomestations.push(templocal);
                    }
                }
                stationgetcallback(false, regbus);
            });
            
        } 
    };

    /* update both bus and station html element */
    var updatebus = function(regbus) {
        $scope.options.allbus = [];
        for (var i=0; i<allbuslocal.length; i++) {
            $scope.options.allbus.push(allbuslocal[i]);
            if (regbus.tocompbus.id == allbuslocal[i].id) {
                $scope.regbus.tocomp = allbuslocal[i];
            }
            if (regbus.tohomebus.id == allbuslocal[i].id) {
                $scope.regbus.tohome = allbuslocal[i];
            }
        }
        if ($scope.regbus.tocomp == null) {
            $scope.regbus.tocomp = $scope.options.allbus[0];
        }
        if ($scope.regbus.tohome == null) {
            $scope.regbus.tohome = $scope.options.allbus[0];
        }
    };

    /* search location complete callback */
    var srchloccomp = function (res) {
        marker = MapService.srchloccomplete(true);
        $scope.loadctrl.srchloc = false;

        /* handle recommend route if needed */
        if (true == recroutestate.inrecroute) {
            $scope.recroute();
        }
        
        $scope.$apply();
    };

    /* load map complete callback function */
    var loadmapcomplete = function (result) {
        /* update map element in html */
        $scope.loadctrl.mapinfo = false;
        $scope.$apply();
    };

    $scope.loadctrl = {
        businfo: false,
        stationinfo: false,
        mapinfo: false,
        submit: false,
        srchloc: true
    };

    $scope.options = {
        allbus: [],
        tocompstations: [],
        tohomestations: []
    };

    $scope.regbus = {
        tocomp: null,
        tohome: null
    };

    $scope.regstation = {
        tocomp: null,
        tohome: null
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
            zoom: 13
        },
        enableKeyboard: true,
        disableDragging: false,
        enableScrollWheelZoom: true
    };

    $scope.srchres = "";

    $scope.loadmapedit = function (map) {
        $scope.loadctrl.mapinfo = true;
        /* register map object instance to MapService */
        MapService.loadmapedit(map, [], {});

        /* create search object when load map complete */
        MapService.srchloc(true, "suggestId", "searchResultPanel", marker, srchloccomp);

        /* mark end loadmap procedure */
        maptemp = map;
        $scope.loadctrl.mapinfo = false;
    };

    $scope.compbuschange = function(dirtocomp) {
        /* get all station info */
        if (true == dirtocomp) {
            updatestation($scope.regbus.tocomp.id, null, null, false);
        } else {
            updatestation(null, $scope.regbus.tohome.id, null, false);
        }
    };

    /* recommend route handler */
    $scope.recroute = function () {
        if (true == $scope.loadctrl.srchloc) {
            /* there is pending srclocation procedure, handle after procedure complete */
            recroutestate.norecroute = false;
            recroutestate.inrecroute = true;
        } else if (null != marker) {
            $scope.loadctrl.srchloc = true;
            recroutestate.norecroute = true;
            recroutestate.inrecroute = false;
            /* create json data */
            var address = new BusinfoService();
            address.lng = marker.getPosition().lng;
            address.lat = marker.getPosition().lat;

            /* POST to server for calculation */
            $scope.loadctrl.businfo = true;
            $scope.loadctrl.stationinfo = true;
            address.$getrecroute(function (res){
                var result = JSON.stringify(res);
                if (result.indexOf('ERROR') != -1) {
                    /* do nothing currently */
                } else {
                    /* get the best route from server */
                    /* update register bus element in html */
                    $scope.loadctrl.businfo = false;
                    updatebus(res);
                    if (res.tocompbus == "") {
                        var busidcomp = allbus[0].id;
                    } else {
                        var busidcomp = res.tocompbus.id;
                    }
                    if (res.tohomebus == "") {
                        var busidhome = allbus[0].id;
                    } else {
                        var busidhome = res.tohomebus.id;
                    }
                    /* get related to company station and update them in html */
                    updatestation(busidcomp, busidhome, res, true);

                    
                }
            },function (error) {
                /* do nothing currently */
                recroutestate.norecroute = true;
                recroutestate.inrecroute = false;
            });
        }
    };

    initfunc();
})