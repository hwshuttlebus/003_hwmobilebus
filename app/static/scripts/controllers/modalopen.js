'use strict';

angular.module('hwmobilebusApp')
    .controller('modalOpenCtrl', function ($scope, $uibModalInstance, $window, $location, BusinfoService, MapService, InterfService, items) {
        $scope.infotitle = items.title;
        $scope.infocontent = items.content;
        
        $scope.okay = function(){
            $uibModalInstance.close('okay');
            switch (items.proc) {
                case "stationDel":
                    stationDelhandle(items);
                    break;
                case "busDel":
                    busDeletehandle(items);
                    break;
                case "busResp":
                    busResphandle(items);
                    break;
                case "busCancel":
                    busCancehandle(items);
                    break;
                case "suggest":
                    suggesthandle(items);
                    break;
                case "msg":
                    msghandle(items);
                    break;
                case "postDel":
                    postdelhandle(items);
                    break;
                case "applyDel":
                    applydelhandle(items);
                    break;
                case "msgDel":
                    msgdelhandle(items);
                case "applystation":
                    applystationhandle(items);
                default:
                    break;
            }
        };
        $scope.cancel = function () {
            $uibModalInstance.close('cancel');

            switch (items.proc) {
                case "busResp":
                    busResphandle(items);
                    break;
                default:
                    break;
            }
        };


        var busResphandle = function (items) {
            $location.url('/busListEdit');
        };

        var busDeletehandle = function (items) {
            BusinfoService.delbus({id: items.delid}, function (res) {
                $scope.loadctrl.submit = false;
                $window.location.reload();
            }, function (error) {
                $scope.loadctrl.submit = false;
                $window.location.reload();
            });
        };

        var busCancehandle = function (items) {
            $location.url('/busListEdit');
        };

        var suggesthandle = function (items) {
            $window.location.reload();
        };

        var msghandle = function (items) {
            $window.location.reload();
        }

        var applystationhandle = function (items) {
            $scope.loadctrl.submit = true;

            var submitinfo = new BusinfoService()
            submitinfo.station_desc = items.desc;
            submitinfo.station_lng = items.lng;
            submitinfo.station_lat = items.lat;
            //console.log(submitinfo);
            submitinfo.$applystation(function(res) {
                $scope.loadctrl.submit = false;
            });
        };

        var postdelhandle = function (items) {
            $scope.loadctrl.submit = true;
            BusinfoService.delpost({id: items.delid}, function(res) {
                $scope.loadctrl.submit = false;
                $window.location.reload();
            }, function (error) {
                $scope.loadctrl.submit = false;
                $window.location.reload();
            });
        };

        var applydelhandle = function (items) {
            $scope.loadctrl.submit = true;
            BusinfoService.delapply({id: items.delid}, function(res) {
                $scope.loadctrl.submit = false;
                $window.location.reload();
            }, function (error) {
                $scope.loadctrl.submit = false;
                $window.location.reload();
            });
        };

        var msgdelhandle = function (items) {
            BusinfoService.delmsg({id: items.delid}, function (res) {
                $window.location.reload();
            }, function(error) {
                $window.location.reload();
            });
        };

        var stationDelhandle = function (items) {
            $scope.loadctrl.submit = true;
            if ("modifiednewstation" != items.delid) {
                /* delete valid station */
                BusinfoService.delstation({id: items.delid}, function(res) {
                    $window.location.reload();
                    $scope.loadctrl.submit = false;
                }, function(error) {
                    $window.location.reload();
                    $scope.loadctrl.submit = false;
                });
            } else {
                if ($scope.isDirToCompany) {
                    var newstations = $scope.tocompanystations;
                } else {
                    var newstations = $scope.tohomestations;
                }
                for (var i=0; i<newstations.length; i++) {
                    if ((items.delid==newstations[i].id) && (items.deldatetime==newstations[i].datetime)
                        && (items.selectid==newstations[i].selectid)) {
                        newstations.splice(i, 1);
                        InterfService.sortStation(newstations);
                        InterfService.storenewstations(newstations, items.dir);
                        $scope.loadctrl.mapinfo = true;
                        MapService.refreshmap(true, newstations, items.callbackfunc);
                        //$window.location.reload();
                    }
                }
                if (newstations.length < 2) {
                    $scope.loadctrl.mapinfo = false;
                }
                $scope.loadctrl.submit = false;
            }
        }
    });