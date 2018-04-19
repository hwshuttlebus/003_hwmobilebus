#!/usr/bin/env python
import os
from app import create_celery_app, db
from app.models import get_currbj_time, mBus, mStation, mUser, DiagramData, Event, BusDiagramData
from datetime import datetime, timedelta

celery = create_celery_app()

def remove_duplicatedate(inputDiagram):
    newrec = []
    for item in inputDiagram:
        if 0 == len(newrec):
            newrec.append(item)
        else:
            for item2 in newrec:
                findflag = False
                if item2.station_id == item.station_id:
                    findflag = True
                    #find duplicate one, save latter time one
                    if item2.arrive_time < item.arrive_time:
                        newrec.remove(item2)
                        newrec.append(item)
            if False == findflag:
                newrec.append(item)
    #print('remove duplicate diagram result:')
    #for item2 in newrec:
    #    print(str(item2.arrive_time))
    return newrec


def updateCurrNumber(stations, equip_id):
    diagrams = []
    totalNum = 0
    #get all data in current date
    nowtime = get_currbj_time()
    #get all the diagram related to one bus line:
    for station in stations:
        #print('!!!!!!!!!!!current station:'+station.name)
        #find all the diagramdata today
        strprefix = nowtime.strftime('%Y-%m-%dT')
        
        diagramrec = station.diagrams.filter_by(mdate=nowtime.date()).all()
        #print('diagramrec result:')
        for item in diagramrec:
            diagrams.append(item)
            #print('record:')
            #print(str(item.arrive_time))

    #handle for all the get diagram data:
    #calculate current number based on remote EVENT table
    newdiagram = remove_duplicatedate(diagrams)
    #set current number for each item
    for idx, item in enumerate(newdiagram):
        #print('diagram item id:'+ str(item.id))
        if len(newdiagram) > 1:
            if idx == 0:
                arriveboj = item.arrive_time.strftime('%H:%M:%S')
                timestartobj = datetime.strptime(strprefix+arriveboj, '%Y-%m-%dT%H:%M:%S')
                timestartobj = timestartobj-timedelta(minutes=30)
                arriveboj2 = newdiagram[idx+1].arrive_time.strftime('%H:%M:%S')
                timeendobj = datetime.strptime(strprefix+arriveboj2, '%Y-%m-%dT%H:%M:%S')
                #print(str(timestartobj))
                #print(str(timeendobj))
                currentNum =  Event.query.filter(Event.DateTimes.between(timestartobj,timeendobj)).filter_by(CarID=equip_id).count()
                totalNum += currentNum
                #print('44444: '+str(currentNum))
            elif idx <= (len(newdiagram)-2):
                arriveboj = item.arrive_time.strftime('%H:%M:%S')
                timestartobj = datetime.strptime(strprefix+arriveboj, '%Y-%m-%dT%H:%M:%S')
                arriveboj2 = newdiagram[idx+1].arrive_time.strftime('%H:%M:%S')
                timeendobj = datetime.strptime(strprefix+arriveboj2, '%Y-%m-%dT%H:%M:%S')
                #print(str(timestartobj))
                #print(str(timeendobj))
                currentNum =  Event.query.filter(Event.DateTimes.between(timestartobj,timeendobj)).filter_by(CarID=equip_id).count()
                totalNum += currentNum
                #print('55555: '+str(currentNum))
        else:
            #there only one record
            arriveboj = item.arrive_time.strftime('%H:%M:%S')
            timestartobj = datetime.strptime(strprefix+arriveboj, '%Y-%m-%dT%H:%M:%S')
            timeendobj = timestartobj + timedelta(minutes=30)
            #print(str(timestartobj))
            #print(str(timeendobj))
            currentNum =  Event.query.filter(Event.DateTimes.between(timestartobj,timeendobj)).filter_by(CarID=equip_id).count()
            totalNum = currentNum
            #print('66666: '+str(currentNum))

        item.current_num = currentNum
        db.session.add(item)
        db.session.commit()
        #print('add to database:')
        #print(item.to_json())

    #update bus diagram
    busid = stations[0].bus_id
    if True == stations[0].dirtocompany:
        busdiagram = stations[-1].diagrams.filter_by(mdate=nowtime.date()).first()
    else:
        busdiagram = stations[0].diagrams.filter_by(mdate=nowtime.date()).first()
    
    if busdiagram is not None:
        print('busdiagram is not None!!')
        print('busdiagram.id:'+str(busdiagram.id))
        busdatarec = BusDiagramData.query.filter_by(mdate=busdiagram.mdate, bus_id=busid).first()
        if busdatarec is not None:
            #update
            busdatarec.tocomp_num = totalNum
        else:
            #new
            if True == stations[0].dirtocompany:
                busdatarec = BusDiagramData(mdate=busdiagram.mdate, arrive_time=busdiagram.arrive_time,
                                            tocomp_num=totalNum, tohome_num=0, bus_id=busid)
                
            else:
                busdatarec = BusDiagramData(mdate=busdiagram.mdate, arrive_time=busdiagram.arrive_time,
                                            tocomp_num=0, tohome_num=totalNum, bus_id=busid)
        db.session.add(busdatarec)
        db.session.commit()
        print('bus diagram add to database:')
        print(busdatarec.to_json())


@celery.task()
def cleangps(inputdata):
    nowtime = get_currbj_time()
    print('11111111')

    #transfer to datetime object
    strprefix = nowtime.strftime('%Y-%m-%dT')

    busrec = mBus.query.all()
    for item in busrec:
        stationrec = item.stations.all()
        tohmstartStation = None
        tohmendStation = None
        tocmpstartStation = None
        tocmpendStation = None
        for item2 in stationrec:
            #find to home start and to company start station
            if item2.dirtocompany == True:
                if tocmpstartStation is None:
                    tocmpstartStation = item2
                elif item2.time < tocmpstartStation.time:
                    tocmpstartStation = item2

                if tocmpendStation is None:
                    tocmpendStation = item2
                elif item2.time > tocmpendStation.time:
                    tocmpendStation = item2
            else:
                if tohmstartStation is None:
                    tohmstartStation = item2
                elif item2.time < tohmstartStation.time:
                    tohmstartStation = item2

                if tohmendStation is None:
                    tohmendStation = item2
                elif item2.time > tohmendStation.time:
                    tohmendStation = item2
        #clean gps data 30 min ahead of bus start time
        nowtime = nowtime.replace(tzinfo=None)

        print(nowtime)
        
        #clean gps data 30 minutes before shuttlbus time or 60 minutes after shuttlebus time
        if tocmpstartStation is not None:
            tocmptime = tocmpstartStation.time.strftime('%H:%M:%S')
            tocmptimeobj = datetime.strptime(strprefix+tocmptime, '%Y-%m-%dT%H:%M:%S')
            print(item.name)
            print(tocmptimeobj)
            if ((nowtime >= (tocmptimeobj-timedelta(minutes=30)))
                and (nowtime <= (tocmptimeobj-timedelta(minutes=10)))):
                item.curridx = 0xFF
                print('clean cmp start ')
        if tocmpendStation is not None:
            tocmptime = tocmpendStation.time.strftime('%H:%M:%S')
            tocmptimeobj = datetime.strptime(strprefix+tocmptime, '%Y-%m-%dT%H:%M:%S')
            print(item.name)
            print(tocmptimeobj)
            if ((nowtime >= (tocmptimeobj+timedelta(minutes=60)))
                and (nowtime <= (tocmptimeobj+timedelta(minutes=80)))):
                item.curridx = 0xFF
                print('clean cmp end ')
        if tohmstartStation is not None:
            tohmtime = tohmstartStation.time.strftime('%H:%M:%S')
            tohmtimeobj = datetime.strptime(strprefix+tohmtime, '%Y-%m-%dT%H:%M:%S')
            print(item.name)
            print(tohmtimeobj)
            if ((nowtime >= (tohmtimeobj-timedelta(minutes=30)))
                and (nowtime <= (tohmtimeobj-timedelta(minutes=10)))):
                item.curridx = 0xFF
                print('clean hm start')
        if tohmendStation is not None:
            tohmtime = tohmendStation.time.strftime('%H:%M:%S')
            tohmtimeobj = datetime.strptime(strprefix+tohmtime, '%Y-%m-%dT%H:%M:%S')
            print(item.name)
            print(tohmtimeobj)
            if ((nowtime >= (tohmtimeobj+timedelta(minutes=60)))
                and (nowtime <= (tohmtimeobj+timedelta(minutes=80)))):
                item.curridx = 0xFF
                print('clean hm end')


@celery.task()
def calcbusdata(inputdata):
    #iterate for equipment id 
    busrec = mBus.query.all()
    for item in busrec:
        print('bus:'+item.name)
        stationup = []
        stationdown = []
        #handle for stations belong to each bus 
        stations = item.stations.order_by(mStation.time).all()
        for item2 in stations:
            if (True == item2.dirtocompany):
                stationup.append(item2)
            else:
                stationdown.append(item2)
        #try:
        updateCurrNumber(stationup, item.equip_id)
        #except Exception as e:
        #    print('%s' %e)

        #try:
        updateCurrNumber(stationdown, item.equip_id)
        #except Exception as e:
        #    print('%s' %e)


@celery.task()
def unconfirmemployee(inputdata):
    #get now time
    nowtime = get_currbj_time()
    nowtime = nowtime.replace(tzinfo=None)

    allemployee = mUser.query.all()
    for item in allemployee:
        #judge register more than half year then clean it
        if (nowtime - item.member_since > timedelta(days=180)):
            item.confirmed = False
            print('Employ:'+item.mailaddr+' is unconfirmed!')