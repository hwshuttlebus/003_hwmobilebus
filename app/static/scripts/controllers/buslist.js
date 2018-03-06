'use strict';

angular.module('hwmobilebusApp')
    .controller('BuslistCtrl', function($scope, $location, BusinfoService, InterfService) {
    
    var allbuslocal={};
    $scope.campusradio = "libingroad";
    $scope.searchbus = [];
    $scope.loadctrl = {
        submit: true
    };

    /* init function */
    var initfunc = function () {
        /* get all bus info */
        BusinfoService.getallbus({}, function(allbus) {
        allbuslocal = allbus;
        /* for to updateebus in the first time get all bus info */
        updateebus();
        /* collect all search result */
        updatesrch();
        $scope.loadctrl.submit = false;
        });
        
    };

    var updateebus = function() {
        $scope.allbus = [];
        for (var i=0; i<allbuslocal.length; i++) {
        if ($scope.campusradio == allbuslocal[i].campus) {
            $scope.allbus.push(allbuslocal[i]);
        }
        }
    };
    
    var updatesrch = function () {
        for (var i=0; i<allbuslocal.length; i++) {
        var busrec = {
            srchstring:null,
            index:null
        }
        busrec.srchstring = allbuslocal[i].number+' '+allbuslocal[i].name;
        busrec.index = i;
        $scope.searchbus.push(busrec);
        }
    }

    $scope.$watchCollection("campusradio", function() {
        updateebus();
    });

    $scope.selsearch = function ($item, $model, $label) {
        InterfService.setbusid(allbuslocal[$item.index].id);
        $location.url('/currentlocation');
    };

    initfunc();
    
    
});