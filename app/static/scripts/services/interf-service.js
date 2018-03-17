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

    /* common function to sort station by time */
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
      };

    /* common function to generate default station for company campus */
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

    /*
    this.isshuttlebustime = function () {
        var currtime = new Date("2018-03-07T07:47:00");
        var temptime;
        var timestring = {
            towkstart: "06:30:00",
            towkend: "10:00:00",
            tohmstart: "17:00:00",
            tohmend: "20:00:00"
        };
        var timeobj = {
            towkstart: null,
            towkend: null,
            tohmstart: null,
            tohmend: null
        }
        
        temptime = currtime.getFullYear()+'-'+((currtime.getMonth() < 10)?"0":"")+(currtime.getMonth()+1)+'-'+((currtime.getDate() < 10)?"0":"")+currtime.getDate()+'T';
        timeobj.towkstart = new Date(temptime+timestring.towkstart);
        timeobj.towkend = new Date(temptime+timestring.towkend);
        timeobj.tohmstart = new Date(temptime+timestring.tohmstart);
        timeobj.tohmend = new Date(temptime+timestring.tohmend);
        
        if ((currtime >= timeobj.towkstart) && (currtime <= timeobj.towkend)) {
            return true;
        }
        else if ((currtime >= timeobj.tohmstart) && (currtime <= timeobj.tohmend)) {
            return true;
        }
        else {
            return false;
        }
    };
    */
});