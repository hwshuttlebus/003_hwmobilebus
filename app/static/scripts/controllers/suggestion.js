'use strict';

angular.module('hwmobilebusApp')
    .controller('SuggestionCtrl', function($scope, $uibModal, BusinfoService, InterfService) {
    var userinfo = {
        id: null,
        role: null
    };
    var postinfo = {
        prevpage: 0,
        nextpage: 0
    }

    $scope.loadctrl = {
        submit: false
    };

    
    $scope.page = {
        Perpage: 0,
        TotalCount: 0,
        CurrentPage: 0,
        maxSize: 5
    };

    var updateuserpost = function(posts) {
        $scope.userpost = [];
        for (var i=0; i<posts.length; i++) {
            var singlepost = {};
            singlepost.body = posts[i].body;
            singlepost.time = posts[i].timestamp;
            singlepost.mailaddr = posts[i].author_mailaddr;
            singlepost.author = posts[i].author;
            singlepost.id = posts[i].id;
            $scope.userpost.push(singlepost);
        }
    };

    var updatepageinfo = function(prev, count, perpage) {
        $scope.page.CurrentPage = prev+1;
        $scope.page.Perpage = perpage;
        $scope.page.TotalCount = count;
    };

    var updatepost = function (userinfo) {
        if (userinfo.role == "Administrator") {
            if (0 == $scope.page.CurrentPage) {
                var qparam = {};
            } else {
                var qparam = {page: $scope.page.CurrentPage}
            }
            BusinfoService.getallpost(qparam, function(allpost) {
                /* update user post */
                updateuserpost(allpost.posts);
                /* update page info */
                updatepageinfo(allpost.prevpage, allpost.count, allpost.perpage);
                $scope.loadctrl.submit = false;
            });
        } else {
            if (0 == $scope.page.CurrentPage) {
                var qparam = {id: userinfo.id};
            } else {
                var qparam = {id: userinfo.id, page: $scope.page.CurrentPage}
            }
            BusinfoService.getpostbyuser(qparam, function(userpost) {
                /* update user post */
                updateuserpost(userpost.posts);
                /* update page info */
                updatepageinfo(userpost.prevpage, userpost.count, userpost.perpage);
                $scope.loadctrl.submit = false;
            });
        }
    };

    var initfunc = function () {
        $scope.userpost = null;
        $scope.loadctrl.submit = true;
        /* get current user */
        BusinfoService.getuserid(function(res) {
            $scope.loadctrl.submit = false;
            userinfo.id = res.id;
            userinfo.role = res.role_name;
            updatepost(userinfo);
        });
    };

    $scope.options = {
        suggesttype: ['司机', '班车线路', '乘车环境', '安全', 'mbus应用', '其他']
    };

    $scope.suggesttype = $scope.options.suggesttype[2];

    $scope.submit = function () {
        /* prepare submit data */
        var postinfo = new BusinfoService();
        postinfo.body = '[ '+$scope.suggesttype+' ]'+$scope.suggestcontxt
        /* send post info */
        console.log(JSON.stringify(postinfo,null, 4));

        $scope.loadctrl.submit = true;
        postinfo.$postsuggest(function (resp) {
            $scope.loadctrl.submit = false;
            var result = JSON.stringify(resp);
            if (result.indexOf('ERROR') != -1) {
                InterfService.geninfomodal('suggest', '提交失败！', result, 'infoModal.html', 'modalOpenCtrl', 'sm', $scope);
            } else {
                InterfService.geninfomodal('suggest', '提交成功！', '', 'infoModal.html', 'modalOpenCtrl', 'sm', $scope);
            }
        }, function(error) {
            $scope.loadctrl.submit = false;
            InterfService.geninfomodal('suggest', '提交失败！', error.status, 'infoModal.html', 'modalOpenCtrl', 'sm', $scope);
        });
        
    }; 

    $scope.delconfirm = function (postid) {
        var titlelocal = "注意！";
        var contentlocal = "确定要删除该意见反馈吗？";
        var resolve = {
            items: function () {
                return {
                    proc: 'postDel',
                    delid: postid,
                    title: titlelocal,
                    content: contentlocal
                };                
            }
        };
        InterfService.genmodal('infoModal.html', 'modalOpenCtrl', 'sm', resolve, $scope);
    };

    $scope.pageChanged = function () {
        updatepost(userinfo);
    };

    /* call init functio */
    initfunc();
})