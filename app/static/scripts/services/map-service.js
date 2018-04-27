'use strict';

angular.module('hwmobilebusApp')
  .service('MapService', function () {
    var mapnormal = {
        map: null,
        markerarray: [],
        driving: null,
        srchlocal: null,
        srchmarker: null
    };
    var mapedit = {
        map: null,
        markerarray: [],
        driving: null, 
        srchlocal: null,
        srchmarker: null
    };

    var G = function (id) {
		return document.getElementById(id);
	}

    this.loadmap = function (map, stations, completefunc) {
        mapnormal.map = map;
        loadroute(mapnormal, stations, completefunc);
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
            var maplocal = mapnormal;
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
        if (null != map.driving) {
            map.driving.clearResults();
        }
    };

    /* create route */
    var loadroute = function (mapobj, inputstations, completefunc) {
        var localmap = mapobj.map;
        var pointArray = new Array();
        var stations = inputstations;
        var markerarray = [];

        for (var loopi=0; loopi<stations.length;loopi++){
            pointArray[loopi] = new BMap.Point(stations[loopi].lon, stations[loopi].lat);
        }

        /* save internal stations(except start/end station) */
        var parray2 = [];
        for (loopi=1; loopi<pointArray.length-1; loopi++) {
            parray2.push(pointArray[loopi]);
        }

        var driving = new BMap.DrivingRoute(localmap, {renderOptions:{map: localmap},autoViewport: true, 
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
                        localmap.removeOverlay(res[loopj].marker);
                        localmap.addOverlay(myPoint);
                    } else {
                        /* for all the internal stations */
                        res[loopj].Pm.Yc.innerHTML=wayPointIconHtml;
                        localmap.addOverlay(myPoint);
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
            localmap.addOverlay(myPoint);
            mapobj.markerarray = markerarray;
        }
    };
    /* create marker for map edit */
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
    };

    this.removemarker = function (ismapedit, marker) {
        if (null != marker) {
            if (true == ismapedit) {
                mapedit.map.removeOverlay(marker);
            } else {
                mapnormal.map.removeOverlay(marker);
            }
        }
    };

    this.getDist = function(ismapedit, point1, point2) {
        if (false == ismapedit) {
            var maplocal = mapnormal.map;
        } else {
            var maplocal = mapedit.map;
        }
        var pttarget = new BMap.Point(point1.lon, point1.lat);
        var ptsrc = new BMap.Point(point2.lon, point2.lat);
        var dist = (maplocal.getDistance(ptsrc, pttarget)).toFixed(2);
        return dist;
    }

    this.updatemarker = function (ismapedit, oldmarker, lon, lat) {
        if (null != oldmarker) {
            this.removemarker(ismapedit, oldmarker);
        }
        var point = new BMap.Point(lon, lat);
        //var iconpath = "/static/images/mappoint.png";

        
        //var IconEntity = new BMap.Icon(iconpath, new BMap.Size(50, 36));
        //var newmarker = new BMap.Marker(point, {icon: IconEntity});
        var newmarker = new BMap.Marker(point);
        if (false == ismapedit) {
            mapnormal.map.addOverlay(newmarker);
        } else {
            mapedit.map.addOverlay(newmarker);
        }
        
        return newmarker;
    }
    /* get duration from search result */
    this.getdurationfromResult = function (results) {
        var plan = results.getPlan(0);
		return plan.getDuration(true);
    };
    /* get distance from search result */
    this.getDistancefromResult = function(results) {
        var plan = results.getPlan(0);
        return plan.getDistance(true);
    };


    /* search location complete callback used for map side */
    this.srchloccomplete = function(ismapedit) {
        if (false == ismapedit) {
            var maplocal = mapnormal.map;
        } else {
            var maplocal = mapedit.map;
        }

        var pp = maplocal.srchlocal.getResults().getPoi(0).point;
        maplocal.centerAndZoom(pp, 15);
        /* create new marker on map based on search result point */
        var newmarker = new BMap.Marker(pp);
        maplocal.addOverlay(newmarker);

        /* record to local */
        maplocal.srchmarker = newmarker;

        /* return newmarker */
        return newmarker;
    };

    /* search location on map */
    var setsrchplace = function (ismapedit, myValue, srchcompletefunc) {
        if (false == ismapedit) {
            var maplocal = mapnormal.map;
        } else {
            var maplocal = mapedit.map;
        }
        /* remove previous search result marker if exists */
        maplocal.removeOverlay(maplocal.srchmarker);

        /* enter search procedure */
        var local = new BMap.LocalSearch(maplocal, {
            onSearchComplete: srchcompletefunc
        });
        local.search(myValue);

        /* record local */
        maplocal.srchlocal = local;
    };

    /* create search location object */
    this.srchloc = function (ismapedit, input, searchResultPanel, srchcompletefunc) {
        var retobj = null;
        if (false == ismapedit) {
            var maplocal = mapnormal.map;
        } else {
            var maplocal = mapedit.map;
        }

        /* set up a autocomplete object */
        var ac = new BMap.Autocomplete(
            {"input" : input
            ,"location" : map
        });
        /* mouse under pulldown menu event handle */
        ac.addEventListener("onhighlight", function(e) { 
        var str = "";
            var _value = e.fromitem.value;
            var value = "";
            if (e.fromitem.index > -1) {
                value = _value.province +  _value.city +  _value.district +  _value.street +  _value.business;
            }    
            str = "FromItem<br />index = " + e.fromitem.index + "<br />value = " + value;
            
            value = "";
            if (e.toitem.index > -1) {
                _value = e.toitem.value;
                value = _value.province +  _value.city +  _value.district +  _value.street +  _value.business;
            }    
            str += "<br />ToItem<br />index = " + e.toitem.index + "<br />value = " + value;
            G(searchResultPanel).innerHTML = str;
        });
        /* mouse click on pull down menu event handle */
        var myValue;
        ac.addEventListener("onconfirm", function(e) {
        var _value = e.item.value;
            myValue = _value.province +  _value.city +  _value.district +  _value.street +  _value.business;
            G(searchResultPanel).innerHTML ="onconfirm<br />index = " + e.item.index + "<br />myValue = " + myValue;
            /* return search location object */
            setsrchplace(ismapedit, myValue, srchcompletefunc);
            
        });
    };

    


    /*
    this.getnearstation = function (ismapedit, stations, point) {
        var ptsrc;
        var dist=0;
        var disttarget=0;
        var retidx=0;
        if (false == ismapedit) {
            var maplocal = map.map;
        } else {
            var maplocal = mapedit.map;
        }

        var pttarget = new BMap.Point(point.lng, point.lat);
        for (var i=0; i<stations.length; i++) {
            ptsrc = new BMap.Point(stations[i].lon, stations[i].lat);
            dist = (maplocal.getDistance(ptsrc, pttarget)).toFixed(2);
            dist = parseFloat(dist);
            if (0==i) {
                disttarget = dist;
            }else if (dist < disttarget) {
                retidx = i;
                disttarget = dist;
            }
        }
        return retidx;
    };
    */
  });
