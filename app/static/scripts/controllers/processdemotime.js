'use strict';

/**
 * @ngdoc function
 * @name hwmobilebusApp.controller:busAnalysisCtrl
 * @description
 * # busAnalysisCtrl
 * Controller of the hwmobilebusApp
 */
angular.module('hwmobilebusApp')
  .controller('busAnalysisCtrl', function ($scope, $location, BusinfoService,InterfService,dataAService ) {
    
    $scope.options = {
      seatOrder:[{id:"busNo",value:"排序：按车次"},{id:"high",value:"排序：从高到低"},{id:"low",value:"排序：从低到高"}],
      arrivalOrder:[{id:"busNo",value:"排序：按车次"},{id:"high",value:"排序：从高到低"},{id:"low",value:"排序：从低到高"}],

    };

    //var for button initial value
    $scope.datatype = "arrivalrate";  //???
    $scope.obj = {
      seatOrder:"busNo",
      seatCycle:"week",
      arrivalOrder:"busNo",
      arrivalCycle:"week",      
      datatype:"arrivalrate",
      istoCompany:"tocom"
    };
    
    var stus = {
      intl: false,
      busData: false,
      allData: false,
      sWeek: false,
      sMonth: false,
      sHalfY: false,
      aWeek: false,
      aMonth: false,
      aHalfY: false   
    };

    var busDiagramlocal;
    var day = 0;
    $scope.time = 0;
    $scope.num = 0;
    var allbuslocal = [];
    $scope.seatBuslist = [];
    $scope.arrivalBuslist = [];  
    $scope.loadctrl = {
      submit: true
    };
    var isPrepare = {
      inS:false,
      busdata: false,
      alldata:false,
      finS:false
    };
  //Init function to get the data from server  
  var initfunction = function(){

    stus.intl = true;
    stus.allData = false;
    stus.busData = false;
    stus.aHalfY = false;
    stus.aMonth = false;
    stus.aWeek = false;
    stus.sHalfY = false;
    stus.sMonth = false;
    stus.sWeek = false;
    
    
    BusinfoService.getallbus({}, function(allbus) {

      try{
      allbuslocal = allbus;
      /* for to updateebus in the first time get all bus info */
      //updateebus();
      for(var i = 0; i<allbuslocal.length;i++)
      {
        var seatDataup = {};
        var seatDatadown = {};
        var arrivalData = {};
        allbuslocal[i].seatDataup = seatDataup;
        allbuslocal[i].seatDatadown = seatDatadown; 
        allbuslocal[i].arrivalData = arrivalData; 
        var tempVar=allbuslocal[i];

        $scope.arrivalBuslist.push(tempVar);

        $scope.seatBuslist.push(tempVar);

      }
      if($scope.obj.istoCompany=="tohome")
      {
        orderbySeatdown($scope.seatBuslist,$scope.obj.seatOrder);
      }
      else
      {
        orderbySeatup($scope.seatBuslist,$scope.obj.seatOrder);
      }
      orderbyArrival($scope.arrivalBuslist,$scope.obj.arrivalOrder); 
      if(stus.intl ==true)
      {
        stus.busData = true;
      }

      if(stus.allData ==true)
      {
        stus.finS = true;
      }
      } 
      catch(e){
        stus.busData=false;
      }

      if(stus.finS == true)
      {
        dataAService.inputData(allbuslocal,busDiagramlocal.busdataanalysis);
        //addDataInfo(allbuslocal,$scope.dataAnalysis);
       // dataAService.arrivaldatabyCycle($scope.obj.arrivalCycle,$scope.arrivalBuslist);
       // dataAService.seatdatabyCycle($scope.obj.seatCycle,$scope.seatBuslist);
        stus.finS = false;
        stus.allData = false;
        stus.busData = false;
        $scope.loadctrl.submit = false;
      }
      
      });

    var day = 0;
    if($scope.obj.arrivalCycle == "hyear")
    {day=180;}
    else if($scope.obj.arrivalCycle == "month")
    {day = 30;}
    else 
    {day = 7;}
    
    BusinfoService.getBusDiag({daysdelta:day},function(busDiagram){
        // $scope.busData.arrivalData = busDiagram.busdataanalysis;
         try
         {
          busDiagramlocal = busDiagram;
          if(stus.intl ==true)
         {
           stus.allData = true;
         }
   
         if(stus.busData ==true)
         {
           stus.finS = true;
         }       
         }
         catch(e){
           stus.allData = false;
         }
   
         if(stus.finS == true)
         {
          dataAService.inputData(allbuslocal,busDiagramlocal.busdataanalysis);
           //addDataInfo(allbuslocal,$scope.dataAnalysis);
           //dataAService.arrivaldatabyCycle($scope.obj.arrivalCycle,$scope.arrivalBuslist);
           //dataAService.seatdatabyCycle($scope.obj.seatCycle,$scope.seatBuslist);
           stus.finS = false;
           stus.allData = false;
           stus.busData = false;
           $scope.loadctrl.submit = false;
         }
    });

  };



  var addDataInfo = function(allbuslist,alldata){
    for(var i=0;i<allbuslist.length;i++)
    {
      dataAService.dataMatrix(alldata,allbuslist[i]);
    }
  };
  
  var updateebus = function() {
    $scope.allbus = [];
    for (var i=0; i<allbuslocal.length; i++) {
        $scope.allbus.push(allbuslocal[i]);
    }
  };
  //order algorithm
  var orderbybusno = function(par){
    var temp;
    for (var i=0;i<par.length-1;i++) {
      for (var j=i+1; j<par.length; j++) {
        if (par[i].number > par[j].number) {
          temp = par[i];
          par[i] = par[j];
          par[j] = temp;
        }
      }
    }
  };

  var seatupbyhigh = function(par){
    var temp;
    for (var i=0;i<par.length-1;i++) {
      for (var j=i+1; j<par.length; j++) {
        if (par[i].seatDataup.val < par[j].seatDataup.val && par[j].seatDataup.text != "无数据" ) {
          temp = par[i];
          par[i] = par[j];
          par[j] = temp;
        }
      }
    }
  };

  var seatdownbyhigh = function(par){
    var temp;
    for (var i=0;i<par.length-1;i++) {
      for (var j=i+1; j<par.length; j++) {
        if (par[i].seatDatadown.val < par[j].seatDatadown.val && par[j].seatDatadown.text != "无数据" ) {
          temp = par[i];
          par[i] = par[j];
          par[j] = temp;
        }
      }
    }
  };

  var arrivalbyhigh = function(par){
    var temp;
    for (var i=0;i<par.length-1;i++) {
      for (var j=i+1; j<par.length; j++) {
        if ((par[i].arrivalData.val < par[j].arrivalData.val)  && par[j].arrivalData.text != "无数据" ) {
          temp = par[i];
          par[i] = par[j];
          par[j] = temp;
        }
      }
    }
  };

  var seatupbylow = function(par){
    var temp;
    for (var i=0;i<par.length-1;i++) {
      for (var j=i+1; j<par.length; j++) {
        if (((par[i].seatDataup.val > par[j].seatDataup.val)||par[i].seatDataup.text == "无数据") && par[j].seatDataup.text != "无数据" ) {
          temp = par[i];
          par[i] = par[j];
          par[j] = temp;
        }
      }
    }
  };

  var seatdownbylow = function(par){
    var temp;
    for (var i=0;i<par.length-1;i++) {
      for (var j=i+1; j<par.length; j++) {
        if (((par[i].seatDatadown.val > par[j].seatDatadown.val)||par[i].seatDatadown.text == "无数据") && par[j].seatDatadown.text != "无数据" ) {
          temp = par[i];
          par[i] = par[j];
          par[j] = temp;
        }
      }
    }
  };
  var arrivalbylow = function(par){
    var temp;
    for (var i=0;i<par.length-1;i++) {
      for (var j=i+1; j<par.length; j++) {
        if (((par[i].arrivalData.val > par[j].arrivalData.val) ||par[i].arrivalData.text == "无数据")&& par[j].arrivalData.text != "无数据" ) {
          temp = par[i];
          par[i] = par[j];
          par[j] = temp;
        }
      }
    }
  };

    var orderbySeatup = function(par,Otype){
      var temp;
      switch(Otype){
        case "busNo":
        orderbybusno(par);
        break;
        case "high":
        seatupbyhigh(par);
        break;
        case "low":
        seatupbylow(par);
        break;
        default:
        orderbybusno(par);
      }
    };

    
    var orderbySeatdown = function(par,Otype){
      var temp;
      switch(Otype){
        case "busNo":
        orderbybusno(par);
        break;
        case "high":
        seatdownbyhigh(par);
        break;
        case "low":
        seatdownbylow(par); 
        break;
        default:
        orderbybusno(par);
      }
    };
    var orderbyArrival = function(par,Otype){
      var temp;
      switch(Otype){
        case "busNo":
        orderbybusno(par);
        break;
        case "high":
        arrivalbyhigh(par);
        break;
        case "low":
        arrivalbylow(par);
        break;
        default:
        orderbybusno(par);
      }
    };

    $scope.onselect = function (id,num,isSeat,busName) {
    dataAService.data_setbusid(id); 
    dataAService.data_setbusnum(num);   
    dataAService.data_setisSeat(isSeat);
    dataAService.data_setbusName(busName); 
    $location.url('/stationAnalysis');
    };
  
    //watch obj.istoCompany
    $scope.$watchCollection("obj.istoCompany", function() {
      if($scope.obj.istoCompany=="tohome")
      {
        orderbySeatdown($scope.seatBuslist,$scope.obj.seatOrder);
      }
      else
      {
        orderbySeatup($scope.seatBuslist,$scope.obj.seatOrder);
      }
    }); 

    //didplay order function
    $scope.$watchCollection("obj.seatOrder", function() {
      if($scope.obj.istoCompany=="tohome")
      {
        orderbySeatdown($scope.seatBuslist,$scope.obj.seatOrder);
      }
      else
      {
        orderbySeatup($scope.seatBuslist,$scope.obj.seatOrder);
      }
    }); 

    //didplay order function
    
    $scope.$watchCollection("obj.arrivalOrder", function() {

      orderbyArrival($scope.arrivalBuslist,$scope.obj.arrivalOrder);
    }); 
    
    $scope.$watchCollection("obj.arrivalCycle", function() {
      var subflag = false;
      if($scope.loadctrl.submit==true)
      {
        subflag=true;
      }
      else
      {
       $scope.loadctrl.submit = true;
      }
      //dataAService.arrivaldatabyCycle($scope.obj.arrivalCycle,$scope.arrivalBuslist);
      var day = 0;
      if($scope.obj.arrivalCycle == "hyear")
      {day=180;}
      else if($scope.obj.arrivalCycle == "month")
      {day = 30;}
      else 
      {day = 7;}
      BusinfoService.getBusDiag({daysdelta:day},function(busDiagram){
          dataAService.inputData(allbuslocal,busDiagram.busdataanalysis);
          if($scope.obj.istoCompany=="tohome")
          {
            orderbySeatdown($scope.seatBuslist,$scope.obj.seatOrder);
          }
          else
          {
          orderbySeatup($scope.seatBuslist,$scope.obj.seatOrder);
          }
          orderbyArrival($scope.arrivalBuslist,$scope.obj.arrivalOrder);
      });
      $scope.obj.seatCycle = $scope.obj.arrivalCycle;
      $scope.loadctrl.submit = subflag;
    }); 

    $scope.$watchCollection("obj.seatCycle", function() {
      var subflag = false;
      if($scope.loadctrl.submit==true)
      {
        subflag=true;
      }
      else
      {
      $scope.loadctrl.submit = true;
      }
      //dataAService.seatdatabyCycle($scope.obj.seatCycle,$scope.seatBuslist);
      var day = 0;
      if($scope.obj.seatCycle == "hyear")
      {day=180;}
      else if($scope.obj.seatCycle == "month")
      {day = 30;}
      else 
      {day = 7;}
      BusinfoService.getBusDiag({daysdelta:day},function(busDiagram){
          dataAService.inputData(allbuslocal,busDiagram.busdataanalysis);
          if($scope.obj.istoCompany=="tohome")
          {
            orderbySeatdown($scope.seatBuslist,$scope.obj.seatOrder);
          }
          else
          {
            orderbySeatup($scope.seatBuslist,$scope.obj.seatOrder);
          }
          orderbyArrival($scope.arrivalBuslist,$scope.obj.arrivalOrder);
      });
      $scope.obj.arrivalCycle = $scope.obj.seatCycle;
      $scope.loadctrl.submit =  subflag;

    }); 

      initfunction();
  });    
//}); 