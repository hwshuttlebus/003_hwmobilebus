'use strict';

/**
 * @ngdoc function
 * @name hwmobilebusApp.controller:stationAnalysisCtrl
 * @description
 * # stationAnalysisCtrl
 * Controller of the hwmobilebusApp
 */
angular.module('hwmobilebusApp')
  .controller('stationAnalysisCtrl', function ($scope, $location, BusinfoService,dataAService) {

    $scope.seatCycle = "week";
  
    //var for button initial value
    $scope.datatype = "arrivalrate";
    $scope.obj = {
      seatOrder:"busNo",
      seatCycle:"week",
      arrivalOrder:"busNo",
      arrivalCycle:"week",      
      datatype:"arrivalrate"
    };   
    $scope.initbus = {
      bus_id: 1,
      bus_num: 1,
      bus_name: "",
      isSeat: 0,

    };

    var stus = {
      intl: false,
      stationData: false,
      allData: false,
      sWeek: false,
      sMonth: false,
      sHalfY: false,
      aWeek: false,
      aMonth: false,
      aHalfY: false   
    };

    var stationDiagramlocal = [];
    var day = 0;
    $scope.time = 0;
    $scope.num = 0;
    var allbuslocal = [];
    $scope.seatStationlist = [];
    $scope.arrivalStationlist = [];  
    var isPrepare = {
      inS:false,
      stationdata: false,
      alldata:false,
      finS:false
    };
    
    $scope.busid = dataAService.data_getbusid();
    $scope.isSeat = dataAService.data_getisSeat();
    $scope.busName = dataAService.data_getbusName();
    $scope.tohomestations = [];
    $scope.stations=[];

    $scope.loadctrl = {
      submit: true
    };
    var initbusstation = function () {

      $scope.initbus.bus_id = dataAService.data_getbusid();
      $scope.initbus.bus_name = dataAService.data_getbusName();
      $scope.initbus.bus_num = dataAService.data_getbusnum();
      $scope.initbus.isSeat = dataAService.data_getisSeat();
      /* get all station info */
      BusinfoService.getstationinfo({id: $scope.initbus.bus_id}, function (inputstationinfo) {
        var templocal;
        var countup = 0;
        var countdown = 0;
        var stationinfo = [];
        stus.intl = true;
        try{
        stationinfo = inputstationinfo;
 
        for (var i=0; i<stationinfo.length; i++) {
          if (true == stationinfo[i].dirtocompany) {
	  
	          var seatDataup = {};
            var arrivalData = {};
	          stationinfo[i].seatDataup = seatDataup;
            stationinfo[i].arrivalData = arrivalData; 
	  
            /* transfer date string to object */
            templocal = stationinfo[i];
            templocal.datetime = new Date("2018-01-01T"+stationinfo[i].time+":00");
            templocal.icon = "/static/images/"+String.fromCharCode(65+countup)+".png";
            templocal.char = String.fromCharCode(65+countup);
            countup++;
            $scope.stations.push(templocal);
          } else {
            /* transfer date string to object */
            templocal = stationinfo[i];
            templocal.datetime = new Date("2018-01-01T"+stationinfo[i].time+":00");
            templocal.icon = "/static/images/"+String.fromCharCode(65+countdown)+".png";
            templocal.char = String.fromCharCode(65+countdown);
            countdown++;
            $scope.tohomestations.push(templocal);
          }
        }

        if(stus.intl ==true)
        {
          stus.stationData = true;
        }
  
        if(stus.allData ==true)
        {
          stus.finS = true;
        }       
        }
        catch(e){
          stus.allData = false;
        }

        if(stus.finS == true)
        {
         dataAService.inputStatData(stations,stationDiagramlocal);
         stus.finS = false;
         stus.allData = false;
         stus.stationData = false;
         $scope.loadctrl.submit = false;
        }


      }, function (error) {
      });

      if($scope.obj.arrivalCycle == "hyear")
      {day=180;}
      else if($scope.obj.arrivalCycle == "month")
      {day = 30;}
      else 
      {day = 7;}
  
      BusinfoService.getStationDiag({id: $scope.initbus.bus_id,daysdelta:day}, function (stationDiagram){
           try
         {
          for(var i = 0; i<stationDiagram.stationdataanalysis.length;i++) 
          {
            if(stationDiagram.stationdataanalysis[i].dirtocompany==true)
                stationDiagramlocal.push(stationDiagram.stationdataanalysis[i]);
          }   
          if(stus.intl ==true)
         {
           stus.allData = true;
         }
   
         if(stus.stationData ==true)
         {
           stus.finS = true;
         }       
         }
         catch(e){
           stus.allData = false;
         }

         if(stus.finS == true)
         {
          dataAService.inputStatData($scope.stations,stationDiagramlocal);
	        stus.finS = false;
          stus.allData = false;
          stus.stationData = false;
          $scope.loadctrl.submit = false;
         }
      });


    };


    //bus arrival time compute function
    //para: b1="12:12"; b2="12:14:12";
    var diffTime = function(time1,time2){
      var strTime1=time1.split(":");
      var strTime2=time2.split(":"); 
      if(strTime1.length==2 )
      {
        strTime1[2]=0;
      }
      if(strTime2.length==2 )
      {
        strTime2[2]=0;
      }
      var hs=(parseInt(strTime2[0])-parseInt(strTime1[0]))*3600;
      var ms=(parseInt(strTime2[1])-parseInt(strTime1[1]))*60;
      var ss=(parseInt(strTime2[2])-parseInt(strTime1[2]));
      var totals = ((hs+ms+ss)/60).toFixed(0);
      return totals;

    };
    //Test1 
      var b1="12:12";
      var b2="12:14:12";
      var convert= diffTime(b1,b2);

    //the function to define is weekend
    //para: datatime = "2018-01-02";
    var isWeekend = function(daytime){
        var datetime = new Date(daytime.replace(/-/g,"/"));
        if(datetime.getDay()>5)
        {
          return ture;
        }
        else
        {
          return false;
        }
    };
    //test
      var datatime = "2018-01-02";
      var week = isWeekend(datatime);

      


       // $scope.test = $scope.seatData[1].result;//parseFloat(1.1111).toFixed(2);
        //$scope.test = parseFloat(1.1111).toFixed(2);
      $scope.text ="早到or晚到";
      $scope.abc =  $scope.dataAnalysis;


      $scope.$watchCollection("obj.arrivalCycle", function() {
        //dataAService.arrivaldatabyCycle($scope.obj.arrivalCycle,$scope.arrivalBuslist);
        var subflag = false;
        if($scope.loadctrl.submit==true)
        {
          subflag=true;
        }
        else
        {
        $scope.loadctrl.submit = true;
        }
        var day = 0;
        if($scope.obj.arrivalCycle == "hyear")
        {day=180;}
        else if($scope.obj.arrivalCycle == "month")
        {day = 30;}
        else 
        {day = 7;}
        BusinfoService.getStationDiag({id:$scope.initbus.bus_id,daysdelta:day},function(stationDiagram){
            //stationDiagramlocal = stationDiagram.stationdataanalysis;
            
            dataAService.inputStatData($scope.stations, stationDiagram.stationdataanalysis);
            //orderbySeatup($scope.seatBuslist,$scope.obj.seatOrder);
            //orderbyArrival($scope.arrivalBuslist,$scope.obj.arrivalOrder);
        });
        $scope.obj.seatCycle = $scope.obj.arrivalCycle;
        $scope.loadctrl.submit = subflag;
      }); 
  
      $scope.$watchCollection("obj.seatCycle", function() {
        //dataAService.seatdatabyCycle($scope.obj.seatCycle,$scope.seatBuslist);
        var subflag = false;
        if($scope.loadctrl.submit==true)
        {
          subflag=true;
        }
        else
        {
        $scope.loadctrl.submit = true;
        }
        var day = 0;
        if($scope.obj.seatCycle == "hyear")
        {day=180;}
        else if($scope.obj.seatCycle == "month")
        {day = 30;}
        else 
        {day = 7;}
        BusinfoService.getStationDiag({id:$scope.initbus.bus_id,daysdelta:day},function(stationDiagram){
          
          dataAService.inputStatData($scope.stations, stationDiagram.stationdataanalysis);

        });
        $scope.obj.arrivalCycle = $scope.obj.seatCycle;
        $scope.loadctrl.submit = subflag;
  
      }); 




     // initfunction();
      initbusstation();

  });    
//}); 