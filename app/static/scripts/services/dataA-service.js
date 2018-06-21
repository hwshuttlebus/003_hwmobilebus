'use strict';

angular.module('hwmobilebusApp')
    .service('dataAService', function () {
    /* this service will store all the information transfer between controllers */
  
         /*For Data analysis
      busId
      */
      var analysis =[]; 
      analysis.busid = 0;
      analysis.isSeat = 0;

 
  
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
      var datatime = "2018-03-21";
      var week = isWeekend(datatime);

	//distinguish the day type to week, month and halfYear  
  var daytype = function(daytime){
      var today = new Date()
      var datetime = new Date(daytime.replace(/-/g,"/"));
      var timediff = (today-datetime)/(24*3600*1000); 
      if(timediff<8){
        return "week";
      }     
      else if(timediff<31){
        return "month";
      }
      else if(timediff<181){
        return "hyear";
      }
      else{
        return  "out";
      }
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
      var totals = ((hs+ms+ss)/60);
      return totals;

    };
    //Test1 
      var b1="12:12";
      var b2="12:14:12";
      var convert= diffTime(b1,b2);
      this.data_setbusid = function (id) {
        localStorage['hwmobilebusApp.analysis.busid'] = id;
    };
    this.data_setisSeat = function (isSeat) {
        localStorage['hwmobilebusApp.analysis.isSeat'] = isSeat;
    };

    this.data_setbusName = function (busName) {
      localStorage['hwmobilebusApp.analysis.busName'] = busName;
  };

    this.data_setbusnum = function(num){
      localStorage['hwmobilebusApp.analysis.busnum']= num;
    };

    this.data_getbusid = function () {
        return localStorage['hwmobilebusApp.analysis.busid'];
    };
    this.data_getisSeat = function () {
        return localStorage['hwmobilebusApp.analysis.isSeat'];
    };
    this.data_getbusnum = function() {
      return localStorage['hwmobilebusApp.analysis.busnum'];
    };  
  
    this.data_getbusName = function () {
      return localStorage['hwmobilebusApp.analysis.busName'];
  };

	
	/*  "busid":"8",
      "data": [
             {"Daytime":"2018-03-15","currentNum":6,"arriveTime":"07:04:27","totalNum":30,"busTime":"07:02:27"},*/
    this.dataMatrix = function(pardata,parbus){
      var seat_data={
        week:{
          amount:0,
          count:0
        },
        month:{
          amount:0,
          count:0
        },
        hyear:{
          amount:0,
          count:0
        },
        rsl:{
          week:0,
          month:0,
          hyear:0
        }
      };
      var arrival_data={
        week:{
          amount:0,
          count:0
        },
        month:{
          amount:0,
          count:0
        },
        hyear:{
          amount:0,
          count:0
        },
        rsl:{
          week:0,
          month:0,
          hyear:0
        }
      };
      seat_data.week.amount=0;
      seat_data.week.count=0
      for (var i=0; i<pardata.length;i++){
        if(pardata[i].id==parbus.id){
        for(var j=0; j<pardata[i].data.length;j++){
        switch (daytype(pardata[i].data[j].Daytime)){
          case "week":  
             seat_data.week.amount=seat_data.week.amount+pardata[i].data[j].currentNum;
             seat_data.week.count++;
             arrival_data.week.amount=arrival_data.week.amount+diffTime(pardata[i].busTime,pardata[i].data[j].arriveTime);
             arrival_data.week.count++;
          case "month":
          seat_data.month.amount=seat_data.month.amount+pardata[i].data[j].currentNum;
          seat_data.month.count++;
          arrival_data.month.amount=arrival_data.month.amount+diffTime(pardata[i].busTime,pardata[i].data[j].arriveTime);
          arrival_data.month.count++;
          break;
          case "hyear":
          seat_data.hyear.amount=seat_data.hyear.amount+pardata[i].data[j].currentNum;
          seat_data.hyear.count++;
          arrival_data.hyear.amount=arrival_data.hyear.amount+diffTime(pardata[i].busTime,pardata[i].data[j].arriveTime);
          arrival_data.hyear.count++;          
          break;
        }
      }
      seat_data.week.amount=seat_data.week.amount/pardata[i].totalNum;
      seat_data.month.amount=seat_data.month.amount/pardata[i].totalNum;
      seat_data.hyear.amount=seat_data.hyear.amount/pardata[i].totalNum;
      seat_data.week.amount=seat_data.week.amount;
    }}
      //parseFloat($scope.seatData[i].currentNum/$scope.seatData[i].totalSeat).toFixed(4);
      seat_data.rsl.week =(seat_data.week.amount/seat_data.week.count);
      seat_data.rsl.month = ((seat_data.week.amount+seat_data.month.amount)/(seat_data.week.count+seat_data.month.count));
      seat_data.rsl.hyear = ((seat_data.week.amount+seat_data.month.amount+seat_data.hyear.amount)/(seat_data.week.count+seat_data.month.count+seat_data.hyear.count));
      arrival_data.rsl.week = (arrival_data.week.amount/arrival_data.week.count);
      arrival_data.rsl.month = ((arrival_data.week.amount+arrival_data.month.amount)/(arrival_data.week.count+arrival_data.month.count));
      arrival_data.rsl.hyear = ((arrival_data.week.amount+arrival_data.month.amount+arrival_data.hyear.amount)/(arrival_data.week.count+arrival_data.month.count+arrival_data.hyear.count));
      parbus.seatData = seat_data;
      parbus.arrivalData = arrival_data;
    
    };
  
    var percentFun = function(value,n){
      value = Math.floor(value*Math.pow(10,n));
      value = value/Math.pow(10,n-2);
      return value;
    }
    this.seatdatabyCycle = function(cycle,par){
      switch(cycle){
        case "week":
            for(var i=0;i<par.length;i++)
            {
              par[i].seatData.result = par[i].seatData.w;

            }
        break;
        case "month":
            for(var i=0;i<par.length;i++)
            {
              par[i].seatData.result = par[i].seatData.m;
            }        
        break;
        case "hyear":
            for(var i=0;i<par.length;i++)
            {
              par[i].seatData.result = par[i].seatData.hy;
            } 
        break;
        default:
            for(var i=0;i<par.length;i++)
            {
              par[i].seatData.result = par[i].seatData.w;
            }       
        break;
      }
    };

    var arrivalType = function(misTime){
      if(Math.abs(misTime)<10)
      {
        return "info";
      }
      else if(Math.abs(misTime)<=20)
      {
        return "warning";
      }
      else
      {
        return "danger";
      }
    }; 

    var arrivalText = function(misTime){

      if(misTime<0)
      {
         return "晚"+Math.abs(misTime).toFixed(0)+"分";
      }
      else if(misTime==0)
      {
        return "准点";
      }
      else
      {
         return "早"+Math.abs(misTime).toFixed(0)+"分";
      } 
    
    };
   
    var roundFun = function(value,n){
      return Math.round(value*Math.pow(10,n))/Math.pow(10,n);
    }
    this.arrivaldatabyCycle = function(cycle,par){
      switch(cycle){
        case "week":
            for(var i=0;i<par.length;i++)
            {
              par.arrivalData.result = par.arrival.w;

            }
        break;
        case "month":
            for(var i=0;i<par.length;i++)
            {
              par.arrivalData.result = par.arrival.m;
            }        
        break;
        case "hyear":
            for(var i=0;i<par.length;i++)
            {
              par.arrivalData.result = par.arrival.hy;
            } 
        break;
        default:
            for(var i=0;i<par.length;i++)
            {
              if(par[i].arrivalData.rsl.week==null||par[i].arrivalData.rsl.week ==undefined ||isNaN(par[i].arrivalData.rsl.week))
              {
                par[i].arrivalData.resursllt = 0; 
                par[i].arrivalData.text = "无数据";
              }
              else
              {
              par[i].arrivalData.rsl =Math.floor(par[i].arrivalData.rsl.week);
              par[i].arrivalData.type=arrivalType(par[i].arrivalData.result);
              par[i].arrivalData.text=arrivalText(par[i].arrivalData.result);
              }
            }       
        break;
      }

    };   
//dataArray: allbuslocal
//para: diagram
    this.inputData = function (dataArray,para){
      var isfind;
      for (var i=0;i<dataArray.length;i++){
        isfind = false;
        for(var j=0; j<para.length;j++){
          if(dataArray[i].id == para[j].bus_id){
            isfind = true;
            dataArray[i].Data = para[j];
            if(para[j].up_num ==null||para[j].up_num ==undefined ||isNaN(para[j].up_num) )              
            {
              dataArray[i].seatDataup.val = 0;
              dataArray[i].seatDataup.text = "无数据";               
            }
            else
            {
              dataArray[i].seatDataup.val = percentFun(para[j].up_num/para[j].seat_num,4);
              dataArray[i].seatDataup.text = percentFun(para[j].up_num/para[j].seat_num,4).toFixed(2)+"%";
            }
  
            if(para[j].down_num ==null||para[j].down_num ==undefined ||isNaN(para[j].down_num) )              
            {
              dataArray[i].seatDatadown.val = 0;
              dataArray[i].seatDatadown.text = "无数据";               
            }
            else
            {
              dataArray[i].seatDatadown.val = percentFun(para[j].down_num/para[j].seat_num,4);
              dataArray[i].seatDatadown.text = percentFun(para[j].down_num/para[j].seat_num,4).toFixed(2)+"%";
            }   
            
            
            if(para[j].up_arrtime==null||para[j].up_arrtime ==undefined ||isNaN(para[j].up_arrtime))
            {
              dataArray[i].arrivalData.val = 0;
              dataArray[i].arrivalData.result = 0;
              dataArray[i].arrivalData.text = "无数据";
            }
            else
            {
              dataArray[i].arrivalData.val = Math.round(para[j].up_arrtime);
              dataArray[i].arrivalData.type= arrivalType(para[j].up_arrtime);
              dataArray[i].arrivalData.text= arrivalText(para[j].up_arrtime);
              dataArray[i].arrivalData.result = Math.abs(dataArray[i].arrivalData.val);
            }
          }  
        }
        if(isfind == false){
          dataArray[i].seatDataup.val = -10000;
          dataArray[i].seatDataup.text = "无数据"; 
          dataArray[i].seatDatadown.val = -10000;
          dataArray[i].seatDatadown.text = "无数据";    
          dataArray[i].arrivalData.val = -10000;
          dataArray[i].arrivalData.result = 0;
          dataArray[i].arrivalData.text = "无数据";
        }
      }
  
    };
    this.inputStatData = function (dataArray,para){
      var isfind;
      for (var i=0;i<dataArray.length;i++){
        isfind = false;
        for(var j=0; j<para.length;j++){
          if(dataArray[i].id == para[j].station_id){
            isfind = true;
            dataArray[i].Data = para[j];
            if(para[j].num ==null||para[j].num ==undefined ||isNaN(para[j].num) )              
            {
              dataArray[i].seatDataup.val = 0;
              dataArray[i].seatDataup.text = "无数据";               
            }
            else
            {
              dataArray[i].seatDataup.val = percentFun(para[j].num/para[j].seat_num,4);
              dataArray[i].seatDataup.text = percentFun(para[j].num/para[j].seat_num,4).toFixed(2)+"%";
            }
  
            
            if(para[j].arrtime==null||para[j].arrtime ==undefined ||isNaN(para[j].arrtime))
            {
              dataArray[i].arrivalData.val = 0;
              dataArray[i].arrivalData.result = 0;
              dataArray[i].arrivalData.text = "无数据";
            }
            else
            {
              dataArray[i].arrivalData.val = Math.round(para[j].arrtime);
              dataArray[i].arrivalData.type= arrivalType(para[j].arrtime);
              dataArray[i].arrivalData.text= arrivalText(para[j].arrtime);
              dataArray[i].arrivalData.result = Math.abs(dataArray[i].arrivalData.val);
            }
          }  
        }
        if(isfind == false){
          dataArray[i].seatDataup.val = -10000;
          dataArray[i].seatDataup.text = "无数据";    
          dataArray[i].arrivalData.val = -10000;
          dataArray[i].arrivalData.result = 0;
          dataArray[i].arrivalData.text = "无数据";
        }
      }
  
    };

});