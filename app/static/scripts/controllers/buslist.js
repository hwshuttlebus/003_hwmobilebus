'use strict';

angular.module('hwmobilebusApp')
    .controller('BuslistCtrl', function($scope, $location, BusinfoService, InterfService) {
    
    var allbuslocal={};
    var busidcomp = null;
    var busidhome = null;


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
            var singlebus = {};
            if ($scope.campusradio == allbuslocal[i].campus) {
                $scope.allbus.push(allbuslocal[i]);
            }
        }

        if ($scope.allbus.length > 0) {
            /* order by time */
            InterfService.orderbus($scope.allbus);

            /* get register bus info and hard code to them on top of allbus*/
            $scope.loadctrl.submit = true;
            BusinfoService.getregbus({}, function(regbus) {
                $scope.loadctrl.submit = false;
                /* update register bus element in html */
                if (regbus.tocompbus != "")  {
                    if (regbus.tocompcampus == $scope.campusradio) {
                        busidcomp = regbus.tocompbus.id;
                        InterfService.hardcodefirst($scope.allbus, busidcomp);
                        $scope.allbus[0].attr = "normal";
                        $scope.allbus[0].mybusname = "（我的班车）";
                    }
                }
                if (regbus.tohomebus != "") {
                    if ((regbus.tohomebus.id != busidcomp) && (regbus.tohomecampus == $scope.campusradio)) {
                        busidhome = regbus.tohomebus.id;
                        InterfService.hardcodefirst($scope.allbus, busidhome);
                        $scope.allbus[0].attr = "normal";
                        $scope.allbus[0].mybusname = "（我的班车）";
                    }
                } 

            });
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
        $scope.onselect(allbuslocal[$item.index].id);
    };

    $scope.onselect = function (id) {
        InterfService.setbusid(id);
        $scope.pageClass = 'new-left-view';
        $location.url('/busList/currentlocation');
    };

    initfunc();

});