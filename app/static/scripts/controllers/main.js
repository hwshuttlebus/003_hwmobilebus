'use strict';

angular.module('hwmobilebusApp')
    .controller('MainCtrl', function ($scope, $location, $window, InterfService, BusinfoService){
    
    /* loading gif control in html */
    $scope.loadctrl = {
        submit: false
    };

    /* main control in MainCtrl */
    $scope.mainctl = {
        title: "MobileBus",
        attr1: "", 
        userrole: "",
        userid: 0,
        mode: 'NORMAL'
    };

    /* this is called before specific view controller is initiate 
      so we can change the page class before target page is rendered */
    $scope.$on('$routeChangeSuccess', function (e, current, pre) {
        try {
            var currurl = current.$$route.originalPath;
            var prevurl = pre.$$route.originalPath;

            if (currurl != prevurl) {
                /* change page class on init */
                if ((prevurl=='/home') || (currurl.indexOf(prevurl) != -1)) {
                    $scope.pageClass = 'new-right-view';
                } else {
                    $scope.pageClass = 'new-left-view';
                }
            }
        } catch (e){
            console.log("Y0", e);
        }
        
    });

    /* watch for location change, this function is called after the view controller is initiated */
    $scope.$watch(function () {
        return $location.path();
    }, function (newpath, oldpath) {
        if (oldpath != newpath) {
            InterfService.seturl(newpath, oldpath);

            var locationurl = $location.url();
            switch (locationurl) {
                case "/busList":
                    $scope.mainctl.title = "班车实时信息";
                    $scope.mainctl.back ="返回";
                    $scope.mainctl.attr1 = "smallfont";
                    break;
                case "/mybus":
                    $scope.mainctl.title = "我的班车";
                    $scope.mainctl.attr1 = "smallfont";
                    break;
                case "/suggestion":
                    $scope.mainctl.title = "意见反馈";
                    $scope.mainctl.attr1 = "smallfont";
                    break;
                case "/busListEdit":
                    $scope.mainctl.title = "班车管理";
                    $scope.mainctl.attr1 = "smallfont";
                    break;
                case "/home":
                    $scope.mainctl.back ="";
                    $scope.mainctl.title = "Mobilebus";
                    $scope.mainctl.attr1 = "";
                    break;
                default:
                    break;
            }
        }
        
    });

    /* click on back callback */
    $scope.back = function() {
        //$scope.$broadcast('back');
        $window.history.back();
    };

    /* mode change click on callback */
    $scope.changeMode = function (newmode) {
        $scope.mainctl.mode = newmode;
        InterfService.setmode(newmode);
    };

    /* init function */
    var initfunc = function () {
        $scope.loadctrl.submit = true;
        /* init page class */
        $scope.pageClass = 'new-right-view';
        /* get current user */
        BusinfoService.getuserid(function(res) {
            $scope.loadctrl.submit = false;
            $scope.mainctl.userid = res.id;
            $scope.mainctl.userrole = res.role_name;

        });


        /* get current mode */
        $scope.mainctl.mode =  InterfService.getmode();
    };


    initfunc();


});