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
    //var BASE = 'http://www.hwmobilebus.tk:9001/api/v1.0/'
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
        getallbus: {
          method: 'GET',
          isArray: true,
          url: BASE+'mbusdata/BusStation/businfo/',
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
        },
        addbusstation: {
          method: 'POST',
          url: BASE+'mbusdata/BusStation\\/',
        },
        delbus: {
          method: 'POST',
          url: BASE+'mbusdata/BusStation/bus/delete/:id',
          params: {
            id: '@id'
          }
        },
        getuserid: {
          method: 'GET',
          url: BASE+'mbusdata/curruser/',
        },
        postsuggest: {
          method: 'POST',
          url: BASE+'mbusdata/posts\\/'
        },
        getpostbyuser: {
          method: 'GET',
          url: BASE+'mbusdata/users/:id/posts/',
          params: {
            id: '@id'
          }
        },
        getallpost: {
          method: 'GET',
          url: BASE+'mbusdata/getallposts\\/'
        },
        delpost: {
          method: 'POST',
          url: BASE+'mbusdata/delposts/:id',
          params: {
            id: '@id'
          }
        },
        getregbus: {
          method: 'GET',
          url: BASE+'mbusdata/getregbus\\/'
        },
        postregbus: {
          method: 'POST',
          url: BASE+'mbusdata/postregbus\\/'
        },
        getrecroute: {
          method: 'POST',
          url: BASE+'mbusdata/calrecroute\\/'
        },
        applystation: {
          method: 'POST',
          url: BASE+'mbusdata/applystation\\/',
        },
        postmsg: {
          method: 'POST',
          url: BASE+'mbusdata/messages\\/'
        },
        getallmsg: {
          method: 'GET',
          url: BASE+'mbusdata/getallmessages\\/'
        },
        delmsg: {
          method: 'POST',
          url: BASE+'mbusdata/delmessages/:id',
          params: {
            id: '@id'
          }
        }
      });
  });
