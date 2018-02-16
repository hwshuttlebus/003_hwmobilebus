'use strict';

angular.module('hwmobilebusApp')
    .controller('modalOpenCtrl', function ($scope, $uibModalInstance, BusinfoService, delid) {
        $scope.okay = function(){
            /* delete station id */
            $uibModalInstance.close('okay');
            if (0xFE != id) {
                /* delete valid station */
                $BusinfoService.delstation({id: delid});
            }
            
            console.log(delid);
        };
        $scope.cancel = function () {
            $uibModalInstance.close('cancel');
        };
    });