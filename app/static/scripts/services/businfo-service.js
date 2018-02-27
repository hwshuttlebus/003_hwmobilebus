'use strict';

/**
 * @ngdoc service
 * @name hwmobilebusApp.BusinfoService
 * @description
 * # BusinfoService
 * Service in the hwmobilebusApp.
 */
angular.module('hwmobilebusApp')
  .service('BusinfoService', function ($resource) {
    var BASE = 'http://localhost:5000/api/v1.0/';
    /* REST API for query busstation information */
    return $resource(BASE,
      {},
      {
        getbusinfo: {
          method: 'GET',
          url: BASE+'mbusdata/BusStation/bus/:id',
          params: {
            id: '@id'
          }
        },
        getstationinfo: {
          method: 'GET',
          isArray: true,
          url: BASE+'mbusdata/bus/:id/stations',
          params: {
            id: '@id'
          }
        },
        delstation: {
          method: 'POST',
          url: BASE+'mbusdata/BusStation/station/delete/:id',
          params: {
            id: '@id'
          }
        },
        updatestation: {
          method: 'POST',
          url: BASE+'mbusdata/BusStation/:id',
          params: {
            id: '@id'
          }
        }
      });
  });
