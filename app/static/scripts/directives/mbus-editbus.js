'use strict';

/**
 * @ngdoc directive
 * @name hwmobilebusApp.directive:mbusEditbus
 * @description
 * # mbusEditbus
 */
angular.module('hwmobilebusApp')
  .directive('mbusEditbus', function ($uibModal, MapService, BusinfoService) {
    return {
      templateUrl: 'busEdit.html',
      restrict: 'E',
      controller: 'MapeditCtrl',
      scope: {},
      link: function ($scope, $element, $attrs) {
        
      }
    };
  });
