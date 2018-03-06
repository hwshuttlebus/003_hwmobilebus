'use strict';

angular.module('hwmobilebusApp')
  .service('MapService', function () {
    var map = {
        map: null,
        markerarray: [],
        driving: null
    };
    var mapedit = {
        map: null,
        markerarray: [],
        driving: null
    };

    this.loadmap = function (map, stations, completefunc) {
        map.map = map;
        loadroute(map, stations, completefunc);
    };

    this.loadmapedit = function (map, stations, completefunc) {
        mapedit.map = map;
        loadroute(mapedit, stations, completefunc);
    };

    /* refresh map */
    this.refreshmap = function (ismapedit, inputstations, loadmapcomplete) {
        if (true == ismapedit) {
            var maplocal = mapedit;
        } else {
            var maplocal = map;
        }
        /* delete all markers */
        deleteallMarkers(maplocal);
        /* delete all search route */
        removedrivingroute(maplocal);
        /* re-render route and markers */
        loadroute(maplocal, inputstations, loadmapcomplete);
    };
  
    /* delete all Markers */
    var deleteallMarkers = function (map) {
        for (var i=0; i<map.markerarray.length; i++) {
            map.map.removeOverlay(map.markerarray[i]);
        }
    };
  
    /* remove route */
    var removedrivingroute = function (map) {
        map.driving.clearResults();
    };

    /* create route */
    var loadroute = function (mapobj, inputstations, completefunc) {
        map = mapobj.map;
        var pointArray = new Array();
        var stations = inputstations;
        var markerarray = [];

        for (var loopi=0; loopi<stations.length;loopi++){
            pointArray[loopi] = new BMap.Point(stations[loopi].lat,stations[loopi].lon);
        }

        /* save internal stations(except start/end station) */
        var parray2 = [];
        for (loopi=1; loopi<pointArray.length-1; loopi++) {
            parray2.push(pointArray[loopi]);
        }

        var driving = new BMap.DrivingRoute(map, {renderOptions:{map: map},autoViewport: true, 
            policy: BMAP_TRANSIT_POLICY_LEAST_TIME,
            onMarkersSet: function (res) {
                //console.log(res)     
                /* replace marker for all the stations */
                for (var loopj=0; loopj<pointArray.length; loopj++) {
                    
                    var iconpath = "/static/images/"+String.fromCharCode(65+loopj)+'.png';
                    var IconEntity = new BMap.Icon(iconpath, new BMap.Size(23, 36));
                    var wayPointIconHtml='<div style="position: absolute; margin: 0px; padding: 0px; width: 36px; height: 40px; overflow: hidden;"><img src='+iconpath+' style="display: none; border:none;margin-left:-11px; margin-top:-35px; "></div>'
                    var myPoint = new BMap.Marker(pointArray[loopj], {icon: IconEntity});
                    
                    /* record all markers */
                    markerarray.push(myPoint);

                    if (loopj===0 || loopj===pointArray.length-1) {
                        /* for start and end station */
                        map.removeOverlay(res[loopj].marker);
                        map.addOverlay(myPoint);
                    } else {
                        /* for all the internal stations */
                        res[loopj].Nm.Yc.innerHTML=wayPointIconHtml;
                        map.addOverlay(myPoint);
                    }
                    myPoint.addEventListener("click", function () {
                    //console.log(pointArray);
                    });
                }
                mapobj.markerarray = markerarray;
            }
            
        });
        
        /* record driving result */
        mapobj.driving = driving;

        /* 获取marker信息 */
        function showinfo(e) {
            var p = e.target;
            alert("marker: " + p.getPosition().lng + "," + p.getPosition.lat);
        }

        if (pointArray.length>=2) {
            driving.search(pointArray[0], pointArray[pointArray.length-1], {waypoints: parray2});
            /* set callback function for complete use */
            driving.setSearchCompleteCallback(completefunc);
        } else if (pointArray.length == 1){
            /* for add new , only one station is added condition */
            var iconpath = "/static/images/A.png";
            var IconEntity = new BMap.Icon(iconpath, new BMap.Size(23, 36));
            var wayPointIconHtml='<div style="position: absolute; margin: 0px; padding: 0px; width: 36px; height: 40px; overflow: hidden;"><img src='+iconpath+' style="display: none; border:none;margin-left:-11px; margin-top:-35px; "></div>'
            var myPoint = new BMap.Marker(pointArray[0], {icon: IconEntity});
            
            /* record all markers */
            markerarray.push(myPoint);
            map.addOverlay(myPoint);
            mapobj.markerarray = markerarray;
        }
    };

    this.createmarker = function (id, selectid) {
        /* create a dtragable marker on the center of current map */
        var mapCenter = mapedit.map.getCenter();
        var point = new BMap.Point(mapCenter.lng, mapCenter.lat);
        var newmarker = {
            marker: null,
            selectid: 0,
            id: 0
        };
        newmarker.marker = new BMap.Marker(point);
        mapedit.map.addOverlay(newmarker.marker);
        newmarker.marker.setAnimation(BMAP_ANIMATION_DROP);
        newmarker.marker.enableDragging();
        newmarker.selectid = selectid;
        newmarker.id = id;
        return newmarker;
    }

    this.removemarker = function (marker) {
        mapedit.map.removeOverlay(marker);
    }
  });
