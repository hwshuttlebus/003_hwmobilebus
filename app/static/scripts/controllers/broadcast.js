'use strict';

angular.module('hwmobilebusApp')
    .controller('BroadcastCtrl', function ($scope, BcastSocket, BusinfoService, InterfService){

    /* get all messeage from server */
    var updatemsg = function () {
        BusinfoService.getallmsg({}, function(allmsg) {
            /* update user post */
            for (var i=0; i<allmsg.Message.length; i++) {
                var msg = {};
                msg.body = allmsg.Message[i].body;
                msg.time = allmsg.Message[i].timestamp;
                msg.id = allmsg.Message[i].id;
                $scope.bcastctl.allmsg.push(msg);
            }
        });
    };

    /* init function */
    var initfunc = function () {
        updatemsg();
    }


    /* broadcast main control structure */
    $scope.bcastctl = {
        broadcastmsg : "【公告】",
        recvmsg: null,
        sendresult: null,
        allmsg: []
    };

    /* submit broadcast msg */
    $scope.submit = function () {
        console.log('send');
        var str1 = $scope.bcastctl.broadcastmsg;
        var str2 = encodeURIComponent(str1);
        BcastSocket.emit('my_broadcast_event', {data: str2});

        /* post to server */
        var postinfo = new BusinfoService()
        postinfo.body = $scope.bcastctl.broadcastmsg;
        console.log(JSON.stringify(postinfo,null, 4));
        postinfo.$postmsg(function (resp) {
            var result = JSON.stringify(resp);
            if (result.indexOf('ERROR') != -1) {
                InterfService.geninfomodal('msg', '发布失败！', result, 'infoModal.html', 'modalOpenCtrl', 'sm', $scope);
            } else {
                InterfService.geninfomodal('msg', '发布成功！', '消息已在mbus首页实时显示！', 'infoModal.html', 'modalOpenCtrl', 'sm', $scope);
            }
        }, function(error) {
            InterfService.geninfomodal('msg', '发布失败！', error.status, 'infoModal.html', 'modalOpenCtrl', 'sm', $scope);
        });
    };

    /* remove listener when leave the page */
    $scope.$on('$destroy', function (event) {
        BcastSocket.removeAllListeners();
    });

    /* delete message */
    $scope.delconfirm = function (msgid) {
        var titlelocal = "注意！";
        var contentlocal = "确定要删除该公告吗？";
        var resolve = {
            items: function () {
                return {
                    proc: 'msgDel',
                    delid: msgid,
                    title: titlelocal,
                    content: contentlocal
                };                
            }
        };
        InterfService.genmodal('infoModal.html', 'modalOpenCtrl', 'sm', resolve, $scope);
    };

    initfunc();

});
