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