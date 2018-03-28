'use strict';

angular.module('hwmobilebusApp')
    .controller('BuseditCtrl', function($scope, $location, $uibModal, BusinfoService, InterfService) {
    
    var allbuslocal = [];
    var modalInstance = '';
    $scope.campusradio = "libingroad";
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

    var genmodal = function (template, ctrl, size, resolve) {
      modalInstance = $uibModal.open({
          animation: true,
          templateUrl: template,
          controller: ctrl,
          scope: $scope,
          size: size,
          backdrop: 'static',
          resolve: resolve
        });
    };
    var geninfomodal = function (proc, title, content, id, template, ctrl, size) {
      var resolve = {
        items: function () {
          return {
            proc: proc,
            title: title,
            content: content,
            delid: id
          };
        }
      };
      genmodal(template, ctrl, size, resolve);
    };

    $scope.$watchCollection("campusradio", function() {
      updateebus();
    });
    
    $scope.addnewbus = function () {
      InterfService.setbusid("newaddbus");
      InterfService.setcampus($scope.campusradio);
      $location.url('/busEditmain');
    };

    $scope.gotoBus = function (id) {
      $scope.currentbus = id;
    };

    $scope.delbus = function (id) {
      /* pop up modal to ensure manually */
      geninfomodal('busDel', '注意！', '确定要删除该班车以及该班车对应的站点信息吗？', id, 'infoModal.html', 'modalOpenCtrl', 'sm');
    };

    $scope.modifybus = function (id) {
      InterfService.setbusid(id);
      InterfService.setcampus($scope.campusradio);
      $location.url('/busEditmain');
    };

    initfunc();
})