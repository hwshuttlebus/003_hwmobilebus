'use strict';

angular.module('hwmobilebusApp')
    .controller('modalOpenCtrl', function ($scope, $uibModalInstance, $window, BusinfoService, delid) {
        $scope.okay = function(){
            /* delete station id */
            $uibModalInstance.close('okay');
            if (0xFE != delid) {
                /* delete valid station */
                BusinfoService.delstation({id: delid}, function(res) {
                    console.log(delid);
                    $window.location.reload();
                }, function(error) {
                    console.log(error.status);
                    $window.location.reload();
                });
            }
            
        };
        $scope.cancel = function () {
            $uibModalInstance.close('cancel');
        };
    });