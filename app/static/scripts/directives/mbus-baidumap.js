'use strict';

/**
 * @ngdoc directive
 * @name hwmobilebusApp.directive:mbusBaidumap
 * @description
 * # mbusBaidumap
 */
angular.module('hwmobilebusApp')
  .directive('mbusBaidumap', function () {
    return {
      templateUrl: 'static/partials/showmaproute.html',
      restrict: 'E',
      link: function ($scope) {
      }
    };
  });
