'use strict';

angular.module('hwmobilebusApp')
    .service('InterfService', function () {
    /* this service will store all the information transfer between controllers */
    var busid = "newaddbus";
    var stationsTocomp = [];
    var stationsTohome = [];

    this.setbusid = function (newid) {
        localStorage['hwmobilebusApp.busid'] = newid;
    };

    this.getbusid = function () {
        return localStorage['hwmobilebusApp.busid'];
    };

    this.storenewstations = function (stations, dir) {
        if (true == dir) {
            stationsTocomp = stations;
        } else {
            stationsTohome = stations;
        }
    };

    this.getnewstations = function (dir) {
        if (true == dir) {
            return stationsTocomp;
        } else {
            return stationsTohome;
        }
    };

    /* all the following function are common function */
    this.sortStation = function (inputstations, lat, lng) {
        var temp, datetime1, datetime2;
        var stations = inputstations;
        for (var i=0;i<stations.length-1;i++) {
          for (var j=i+1; j<stations.length; j++) {
            if (stations[i].datetime > stations[j].datetime) {
              temp = stations[i];
              stations[i] = stations[j];
              stations[j] = temp;
            }
          }
        }
        /* icon */
        for (var i=0; i<stations.length; i++) {
          stations[i].icon = "/static/images/"+String.fromCharCode(65+i)+".png";
          /* for newly added */
          if (stations[i].id == "newstation") {
            stations[i].id = "modifiednewstation"; /* marked as modified */
            stations[i].lat = lat;
            stations[i].lon = lng;
          }
          stations[i].selectid = i;
        }

        return stations;
      };

    /* function to generate default station for company campus */
    this.gencompstation = function(isDirToComp, lat, lon) {
        var time = "";
        var station = {};
        if (true == isDirToComp) {
          time = "08:30";
        } else {
          time = "17:15";
        }
        station.id = "company";
        station.time = time;
        station.datetime = new Date("2018-01-01T"+time+":00");
        station.description = "霍尼韦尔";
        station.name = "霍尼韦尔";
        station.lat = lat;
        station.lon = lon;
        station.campus = "libingroad";
        station.dirtocompany = isDirToComp;
  
        return station;
      }
});