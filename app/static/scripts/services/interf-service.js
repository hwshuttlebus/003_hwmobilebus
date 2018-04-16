'use strict';

angular.module('hwmobilebusApp')
    .service('InterfService', function ($uibModal) {
    /* this service will store all the information transfer between controllers */
    var busid = "newaddbus";
    var stationsTocomp = [];
    var stationsTohome = [];
    var modalInstance = '';
    var currurl = '';
    var prevurl = '';
    var mainctl = {
        mode:  'NORMAL'
    };
    
    /* change mode on home page */
    this.setmode = function (newmode) {
        mainctl.mode = newmode;
    };

    this.getmode = function () {
        return mainctl.mode;
    };

    this.setbusid = function (newid) {
        localStorage['hwmobilebusApp.busid'] = newid;
    };

    /* store campus to local storage */
    this.setcampus = function (campus) {
        localStorage['hwmobilebusApp.campus'] = campus;
    };

    this.getbusid = function () {
        return localStorage['hwmobilebusApp.busid'];
    };

    this.getcampus = function () {
        return localStorage['hwmobilebusApp.campus'];
    };

    /* set & get previous page url */
    this.seturl = function (newpath, oldpath) {
        prevurl = oldpath;
        currurl = newpath;
    };
    
    this.getprevurl = function () {
        return prevurl;
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

    this.geninfomodal = function (proc, title, content, template, ctrl, size, scope) {
        var resolve = {
            items: function () {
                return {
                    proc: proc,
                    title: title,
                    content: content
                };
            }
        };
        this.genmodal(template, ctrl, size, resolve, scope);
    };

    this.genmodal = function (template, ctrl, size, resolve, scope) {
        modalInstance = $uibModal.open({
            animation: true,
            templateUrl: template,
            controller: ctrl,
            scope: scope,
            backdrop: 'static',
            size: size,
            resolve: resolve
        });
    };

    /* common function to generate default station for company campus */
    this.gencompstation = function(isDirToComp, lat, lon, campus) {
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
        station.campus = campus;
        station.dirtocompany = isDirToComp;
  
        return station;
      };

    /* common function to generate modal */
    this.geninfomodal = function (proc, title, content, template, ctrl, size, scope) {
        var resolve = {
            items: function () {
            return {
                proc: proc,
                title: title,
                content: content
            };
            }
        };
        this.genmodal(template, ctrl, size, resolve, scope);
    };

    /* order all bus info by bus number ascend */
    this.orderbus = function (allbusinfo) {
        var temp;
        for (var i=0; i<allbusinfo.length-1; i++) {
          for (var j=i+1; j<allbusinfo.length; j++) {
            if (allbusinfo[j].number < allbusinfo[i].number) {
              temp = allbusinfo[i];
              allbusinfo[i] = angular.copy(allbusinfo[j]);
              allbusinfo[j] = temp;
            }
          }
        }
    };

    /* hard code first function */
    this.hardcodefirst = function (allbusinfo, targetid) {
        var first = null;
        for (var i=0; i<allbusinfo.length; i++) {
            if (targetid == allbusinfo[i].id) {
                first = i;
                break;
            }
        }

        if (!first) {
            return allbusinfo;
        }

        var firstEl = allbusinfo[first];
        /* remove find item and append to first */
        allbusinfo.splice(first, 1);
        allbusinfo.unshift(firstEl);
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