from flask import jsonify, request, current_app, url_for
from . import api
from .. models import DiagramData, db, BusDiagramData, get_currbj_time, mBus, mStation, Event
from datetime import datetime, timedelta, date
import datetime as dt
import time

latest_update_date=date(2019,1,1)

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


def updateNumberForBusDate(bus, expectedDate, tocompany):
    diagrams = []
    totalNum = 0
    currentNum = 0
    stations = bus.stations.filter_by(dirtocompany=tocompany).order_by(mStation.time).all()
    #get all the diagram related to one bus line:
    for station in stations:
        #print('!!!!!!!!!!!current station:'+station.name)
        #find all the diagramdata today
        strprefix = expectedDate.strftime('%Y-%m-%dT')

        diagramrec = station.diagrams.filter_by(mdate=expectedDate).all()
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
                currentNum =  Event.query.filter(Event.DateTimes.between(timestartobj,timeendobj)).filter_by(CarID=bus.number).count()
                totalNum += currentNum
                #print('44444: '+str(currentNum))
            elif idx <= (len(newdiagram)-2):
                arriveboj = item.arrive_time.strftime('%H:%M:%S')
                timestartobj = datetime.strptime(strprefix+arriveboj, '%Y-%m-%dT%H:%M:%S')
                arriveboj2 = newdiagram[idx+1].arrive_time.strftime('%H:%M:%S')
                timeendobj = datetime.strptime(strprefix+arriveboj2, '%Y-%m-%dT%H:%M:%S')
                #print(str(timestartobj))
                #print(str(timeendobj))
                currentNum =  Event.query.filter(Event.DateTimes.between(timestartobj,timeendobj)).filter_by(CarID=bus.number).count()
                totalNum += currentNum
                #print('55555: '+str(currentNum))
        else:
            #there only one record
            arriveboj = item.arrive_time.strftime('%H:%M:%S')
            timestartobj = datetime.strptime(strprefix+arriveboj, '%Y-%m-%dT%H:%M:%S')
            timeendobj = timestartobj + timedelta(minutes=30)
            #print(str(timestartobj))
            #print(str(timeendobj))
            currentNum =  Event.query.filter(Event.DateTimes.between(timestartobj,timeendobj)).filter_by(CarID=bus.number).count()
            totalNum = currentNum
            #print('66666: '+str(currentNum))

        if currentNum != 0:
            item.current_num = currentNum
            db.session.add(item)
            db.session.commit()
    #print('add to database:')
    #print(item.to_json())

    #update bus diagram
    busid = stations[0].bus_id
    if True == stations[0].dirtocompany:
        busdiagram = stations[-1].diagrams.filter_by(mdate=expectedDate).first()
    else:
        busdiagram = stations[0].diagrams.filter_by(mdate=expectedDate).first()

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
        print('bus diagram add to database, bus number:{}'.format(bus.number))
        print(busdatarec.to_json())

def updateNumber():
    global latest_update_date
    nowtime = get_currbj_time()
    today = nowtime.date()
    latest_update_date2 = DiagramData.query.order_by(db.desc(DiagramData.mdate)).filter(DiagramData.current_num != 0).first().mdate
    daynumber = min(today - latest_update_date, today - latest_update_date2, timedelta(days=180))
    daynumber = max(daynumber.days, 0)
    busrec = mBus.query.all()
    for bus in busrec:
        for d in (today - timedelta(n) for n in range(daynumber)):
            updateNumberForBusDate(bus, d, 1)
            updateNumberForBusDate(bus, d, 0)
    latest_update_date = today

def dataanalysis(daysdelta, targetstation):
    updateNumber()
    nowtime = get_currbj_time()
    resultarray = []

    for item in targetstation:
        diagrams = DiagramData.query.filter(DiagramData.mdate.between((nowtime.date()-timedelta(days=daysdelta)), nowtime.date())).filter_by(station_id=item.id)
        count = 0
        count2 = 0
        totalnum = 0
        targetnum = 0
        totalarrtime = 0
        for item2 in diagrams:
            #arrive number
            if item2.current_num != 0:
                count += 1
                totalnum += item2.current_num
            #arrive time
            t1 = dt.datetime.combine(dt.date(2018,1,1), item2.arrive_time)
            t1 = time.mktime(t1.timetuple())
            t2 = dt.datetime.combine(dt.date(2018,1,1), item.time)
            t2 = time.mktime(t2.timetuple())
            print('t2: '+ str(t2))
            print('t1:' + str(t1))
            arrtime = (t2 - t1)/60
            totalarrtime += arrtime
            count2 += 1
            print('arrtime: '+str(arrtime))
        if count2 != 0:
            targetarrtime = totalarrtime/count2
            if count != 0:
                targetnum = totalnum/count
            busrec = mBus.query.filter_by(id=item.bus_id).first()
            seat_num = busrec.seat_num
            resultarray.append((item.id, item.bus_id, targetarrtime,
                                targetnum, item.dirtocompany, seat_num, item.time.strftime('%H:%M')))
    return resultarray


#append data in source to target, input srcdata should be list type
def appenddata(srcdata, isappendbus):
    tgtdata = []
    if True == isappendbus:
        for item in srcdata:
            if True == item[4]:
                numdown = 0
                #find the to home station
                for item2 in srcdata:
                    #bus id equal
                    if (item2[1] == item[1]) and (False == item2[4]):
                        numdown = item2[3]
                singlejson = {
                    'bus_id' : item[1],
                    'seat_num':item[5],
                    'up_station_id': item[0],
                    'up_arrtime':item[2],
                    'up_num':item[3],
                    'down_num':numdown,
                    'up_station_time': item[6]
                }
                tgtdata.append(singlejson)
    else:
        for item in srcdata:
            singlejson = {
                'bus_id': item[1],
                'seat_num': item[5],
                'station_id': item[0],
                'arrtime': item[2],
                'num': item[3],
                'dirtocompany': item[4],
                'station_time': item[6]
            }
            tgtdata.append(singlejson)
    return tgtdata

@api.route('/mbusdata/busdataanalysis/')
def bus_analysis():
    #get all target station id list
    #final station on to company direction
    #first station on to home direction
    daysdelta = request.args.get('daysdelta', 180, type=int)

    targetstation = []
    allbus = mBus.query.all()
    if allbus is not None:
        for bus in allbus:
            allstations = bus.stations.order_by(mStation.time).all()
            stationup = []
            stationdown = []
            if allstations is not None:
                for station in allstations:
                    if True == station.dirtocompany:
                        stationup.append(station)
                    else:
                        stationdown.append(station)
                if len(stationup) > 0:
                    targetstation.append(stationup[-1])
                if len(stationdown) > 0:
                    targetstation.append(stationdown[0])

    #analysis data
    dataresult = dataanalysis(daysdelta, targetstation)
    print(dataresult)

    #transfer to json format
    retarray = appenddata(dataresult, True)
    return jsonify({'busdataanalysis':retarray})


@api.route('/mbusdata/stationdataanalysis/<int:id>/')
def station_analysis(id):
    #find bus
    busrec = mBus.query.get_or_404(id)
    #calculate for all stations
    daysdelta = request.args.get('daysdelta', 180, type=int)

    targetstation = busrec.stations.order_by(mStation.time).all()
    dataresult = dataanalysis(daysdelta, targetstation)

    #transfer to json format
    retarray = appenddata(dataresult, False)
    return jsonify({'stationdataanalysis':retarray})

@api.route('/mbusdata/diagramdata/', methods=['POST'])
def post_diagramdata():
    diagram = DiagramData.from_json(request.json)
    diagramrec = DiagramData.query.filter_by(arrive_time=diagram.arrive_time)
    if diagramrec is not None:
        diagramrec.mdate = diagram.mdate
        diagramrec.arrive_time = diagram.arrive_time
        diagramrec.current_num = diagram.current_num
    else:
        diagramrec = diagram

    station = mStation.query.filter_by(id=diagram.station_id).first()
    if station is not None:
        diagramrec.mstation = station
    else:
        return jsonify({'invalid mstation id: ' : 'ERROR'})

    db.session.add(diagramrec)
    db.session.commit()
    return jsonify(diagramrec.to_json())


@api.route('/mbusdata/getalldiagram/')
def get_alldiagram():
    page = request.args.get('page', 1, type=int)

    nowtime = get_currbj_time()
    pagination = DiagramData.query.filter(DiagramData.mdate.between((nowtime.date()-timedelta(days=180)), nowtime.date())).paginate(
                            page, per_page=current_app.config['MBUS_POSTS_PER_PAGE'],
                            error_out=False)
    diagrams = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_alldiagram', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_alldiagram', page=page+1, _external=True)

    return jsonify({
        'data': [diagram.to_json() for diagram in diagrams],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/mbusdata/getbusdiagram/')
def get_busdiagram():
    page = request.args.get('page', 1, type=int)

    nowtime = get_currbj_time()
    pagination = BusDiagramData.query.filter(BusDiagramData.mdate.between((nowtime.date()-timedelta(days=180)), nowtime.date())).paginate(
                            page, per_page=current_app.config['MBUS_POSTS_PER_PAGE'],
                            error_out=False)
    diagrams = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_busdiagram', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_busdiagram', page=page+1, _external=True)

    return jsonify({
        'data': [diagram.to_json() for diagram in diagrams],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
