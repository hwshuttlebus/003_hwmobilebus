'use strict';

angular.module('hwmobilebusApp')
    .controller('EmploymanageCtrl', function ($scope, $location, BusinfoService, InterfService){

    /* employee management controller */
    $scope.empctl={
        page : {
            Perpage: 0,
            TotalCount: 0,
            CurrentPage: 0,
            maxSize: 5
        },
        users:[],
        applys: [],
        usercount : 0
    };

    /* record user info */
    var recordusers = function(users) {
        $scope.empctl.users = [];
        for (var i=0; i<users.length; i++) {
            var user = {};
            user.mailaddr = users[i].mailaddr;
            user.userlink = 'user/'+user.mailaddr;
            user.reg_bus1 = users[i].reg_bus1;
            user.reg_bus2 = users[i].reg_bus2;
            user.reg_station1 = users[i].reg_station1;
            user.reg_station2 = users[i].reg_station2;
            $scope.empctl.users.push(user);
        }

        //$scope.empctl.usercount = $scope.empctl.users.length;
    };

    /* record apply info */
    var recordapply = function (applys) {
        $scope.empctl.applys = [];
        for (var i=0; i<applys.length; i++) {
            var apply = {};
            apply.mailaddr = applys[i].mailaddr;

            /* exclude invalid one */
            if ((true == applys[i].applyflag) && (applys[i].applydesc != "")) {
                apply.id = applys[i].id;
                apply.mailaddr = applys[i].mailaddr;
                apply.applydesc = applys[i].applydesc;
                apply.lat = applys[i].lat;
                apply.lon = applys[i].lon;
            }
            $scope.empctl.applys.push(apply);
        }
    }

    /* update user pagination info in html */
    var updatepageinfo = function(prev, count, perpage) {
        $scope.empctl.page.CurrentPage = prev+1;
        $scope.empctl.page.Perpage = perpage;
        $scope.empctl.page.TotalCount = count;
    };

    var initfunc = function () {
        updateusers();
        updateapply();
    };

    /* get info from server and update in html */
    var updateusers = function () {
        if (0 == $scope.empctl.page.CurrentPage) {
            var qparam = {};
        } else {
            var qparam = {page: $scope.empctl.page.CurrentPage}
        }
        BusinfoService.getalluser(qparam, function(allusers) {
            /* record user post to local */
            recordusers(allusers.users);
            $scope.empctl.usercount = allusers.usercount;
            /* update page info */
            updatepageinfo(allusers.prevpage, allusers.count, allusers.perpage);
        });
    }

    var updateapply = function () {
        BusinfoService.getuserapply({}, function (applyinfo) {
            /* record user apply info to local */
            recordapply(applyinfo.applyresult);
        });
    }


    $scope.pageChanged = function () {
        updateusers();
    };

    /* delete on apply info */
    $scope.delconfirm = function (userid) {
        var titlelocal = "注意！";
        var contentlocal = "确定要删除该申请信息吗？";
        var resolve = {
            items: function () {
                return {
                    proc: 'applyDel',
                    delid: userid,
                    title: titlelocal,
                    content: contentlocal
                };
            }
        };
        InterfService.genmodal('infoModal.html', 'modalOpenCtrl', 'sm', resolve, $scope);
    };

    initfunc();
});
