from . import api
from flask import jsonify, request
from datetime import datetime
from flask_login import current_user
from .authentication import auth
from .. models import db, mStation, mBus, haversine
import time

#update as per bus id
@api.route('/mbusdata/BusStation/<int:id>', methods=['POST'])
def update_mbusinfo(id):
    stationrec1 = []
    stationrec2 = []
    try:
        bus = mBus.from_json(request.json)
        #handle bus information first
        busrec = mBus.query.get_or_404(id)
        #update
        busrec.name = bus.name
        busrec.number = bus.number
        busrec.cz_name = bus.cz_name
        busrec.cz_phone = bus.cz_phone
        busrec.sj_name = bus.sj_name
        busrec.sj_phone = bus.sj_phone
        busrec.seat_num = bus.seat_num
        busrec.equip_id = bus.equip_id
        busrec.recordtime = bus.recordtime
        busrec.color = bus.color
        busrec.buslicense = bus.buslicense
        busrec.campus = bus.campus
    except Exception as e:
        return jsonify({'ERROR occur when try to parse station_to_company structure!': '%s' %e})

    #handle station information next
    #delete all the related station
    stations = busrec.stations.all()
    for item in stations:
        db.session.delete(item)
        db.session.commit()

    #direction: to company
    station_tocompany = request.json.get('station_tocompany')
    if station_tocompany is not None:
        try:
            for item in station_tocompany:
                station1 = mStation.from_json(item, True)
                temp = station1
                #update relationship
                temp.mbus = busrec
                stationrec1.append(temp)
        except Exception as e:
            return jsonify({'ERROR occur when try to parse station_to_company structure!':'%s' %e })

    #direction: to home
    station_tohome = request.json.get('station_tohome')
    if station_tohome is not None:
        try:
            for item in station_tohome:
                station2 = mStation.from_json(item, False)
                temp = station2
                #update relationship
                temp.mbus = busrec
                stationrec2.append(temp)
        except Exception as e:
            return jsonify({'ERROR occur when try to parse station_tohome structure!':'%s' %e })

    db.session.add(busrec)
    db.session.commit()

    for item2 in stationrec1:
        db.session.add(item2)
    for item3 in stationrec2:
        db.session.add(item3)
    db.session.commit()

    return jsonify({'added bus record: ': busrec.to_json(),
                    'added station1 record: ': [item.to_json() for item in stationrec1],
                    'added station2 record: ': [item.to_json() for item in stationrec2]})


#add as per name and campus
@api.route('/mbusdata/BusStation/', methods=['POST'])
def post_mbusinfo():
    stationrec1 = []
    stationrec2 = []
    try:
        bus = mBus.from_json(request.json)

        #handle bus information first
        busrec = mBus.query.filter_by(name=bus.name, campus=bus.campus).first()
        if busrec is not None:
            #update
            busrec.name = bus.name
            busrec.number = bus.number
            busrec.cz_name = bus.cz_name
            busrec.cz_phone = bus.cz_phone
            busrec.sj_name = bus.sj_name
            busrec.sj_phone = bus.sj_phone
            busrec.seat_num = bus.seat_num
            busrec.equip_id = bus.equip_id
            busrec.recordtime = bus.recordtime
            busrec.color = bus.color
            busrec.buslicense = bus.buslicense
            busrec.campus = bus.campus
        else:
            #newly create
            busrec = bus
    except Exception as e:
        return jsonify({'ERROR occur when try to parse station_to_company structure!': '%s' %e})

    #handle station information next
    #direction: to company
    station_tocompany = request.json.get('station_tocompany')
    if station_tocompany is not None:
        try:
            for item in station_tocompany:
                station1 = mStation.from_json(item, True)
                temp = mStation.query.filter_by(name=station1.name, dirtocompany=station1.dirtocompany,
                                                campus=station1.campus).first()
                if temp is not None:
                    temp.name = station1.name
                    temp.description = station1.description
                    temp.time = station1.time
                    temp.dirtocompany = station1.dirtocompany
                    temp.lat = station1.lat
                    temp.lon = station1.lon
                    temp.campus = station1.campus
                else:
                    temp = station1
                #update relationship
                temp.mbus = busrec
                stationrec1.append(temp)
        except Exception as e:
            return jsonify({'ERROR occur when try to parse station_to_company structure!':'%s' %e })

    #direction: to home
    station_tohome = request.json.get('station_tohome')
    if station_tohome is not None:
        try:
            for item in station_tohome:
                station2 = mStation.from_json(item, False)
                temp = mStation.query.filter_by(name=station2.name, dirtocompany=station2.dirtocompany,
                                                campus=station2.campus).first()
                if temp is not None:
                    temp.name = station2.name
                    temp.description = station2.description
                    temp.time = station2.time
                    temp.dirtocompany = station2.dirtocompany
                    temp.lat = station2.lat
                    temp.lon = station2.lon
                    temp.campus = station2.campus
                else:
                    temp = station2
                #update relationship
                temp.mbus = busrec
                stationrec2.append(temp)
        except Exception as e:
            return jsonify({'ERROR occur when try to parse station_tohome structure!':'%s' %e })

    db.session.add(busrec)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'ERROR occur when try to parse station_tohome structure!':'%s' %e })

    for item2 in stationrec1:
        db.session.add(item2)
    for item3 in stationrec2:
        db.session.add(item3)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'ERROR occur when try to parse station_tohome structure!':'%s' %e })

    return jsonify({'added bus record: ': busrec.to_json(),
                    'added station1 record: ': [item.to_json() for item in stationrec1],
                    'added station2 record: ': [item.to_json() for item in stationrec2]})


@api.route('/mbusdata/BusStation/bus/<int:id>', methods=['GET'])
def get_bus(id):
    busrec = mBus.query.get_or_404(id)
    msg = ""
    if busrec.is_working_time():
        if busrec.curridx != 0xFF:
            if busrec.recordtime is not None:
                deltatime = (time.time() - busrec.recordtime.timestamp())/60 # unit minute
                if deltatime > 1:
                    msg = ":车辆GPS信号丢失,持续{}分钟{}秒".format(
                            int(deltatime), int(60*(deltatime - int(deltatime))))
    else:
        if busrec.curridx != 0xFF:
            busrec.curridx = 0xFF
            db.session.add(busrec)
            db.session.commit()
        msg = ":非上下班时间"
    json_dict = busrec.to_json()
    json_dict['msg'] = msg
    #print("!!!bus_number={}, json={}".format(busrec.number, json_dict))
    return jsonify(json_dict)

@api.route('/mbusdata/BusStation/businfo/', methods=['GET'])
def get_allbus():
    returnrec = [];
    busrecs = mBus.query.all()
    for item in busrecs:
        if item.name is not "" and item.name is not None:
            returnrec.append(item.to_json())
    return jsonify(returnrec)

@api.route('/mbusdata/BusStation/bus/delete/<int:id>', methods=['POST'])
def delete_bus(id):
    busrec = mBus.query.filter_by(id=id).first()
    if busrec is not None:
        db.session.delete(busrec)
        db.session.commit()
        return jsonify({'deleted bus:': busrec.to_json()})
    else:
        return jsonify({'ERROR!': 'busrec is None'})

@api.route('/mbusdata/BusStation/station/delete/<int:id>',methods=['POST'])
def delete_station(id):
    stationrec = mStation.query.get_or_404(id)
    db.session.delete(stationrec)
    db.session.commit()
    return jsonify({'deleted station:' : stationrec.to_json()})


@api.route('/mbusdata/calrecroute/', methods=['POST'])
def cal_recommand_route():
    #parse lat/lng
    lng = request.json.get('lng')
    lat = request.json.get('lat')

    #get current user's campus
    campus = current_user.campus
    if campus is not None or campus is not "":
        #iterate all stations and find the near station
        stations = mStation.query.filter_by(campus=campus).all()

    idx, dist = mBus.getnearsation_excomp(stations, lng, lat, True)
    #get related bus and all stations
    tocompstation = None
    tohomestation = None
    bus = mBus.query.filter_by(id=stations[idx].bus_id).first()
    if bus is not None:
        tocompstation = stations[idx]
        stations2 = bus.stations.all()
        idx2, dist2 = mBus.getnearsation_excomp(stations2, lng, lat, False)
        tohomestation = stations2[idx2]
        # print(tohomestation.to_json())
        return jsonify({'tocompbus': bus.to_json(),
                        'tocompstation': tocompstation.to_json(),
                        'tohomebus': bus.to_json(),
                        'tohomestation': tohomestation.to_json()})

    return jsonify({'ERROR!': 'can not find specific bus in calrecroute procedure! '})

@api.route('/mbusdata/bus/<int:id>/stations')
def get_bus_related_stations(id):
    busrec = mBus.query.get_or_404(id)
    stationrecs = busrec.stations
    returnrec = []
    for stationrec in stationrecs:
        returnrec.append(stationrec.to_json())

    '''
    arrCompTime = '8:30'
    LeaveComTime = '17:15'
    arrCampus = busrec.campus
    if arrCampus == 'libingroad':
        lat = 121.620084
        lon = 31.201496
    else:
        lat = 121.609924
        lon = 31.184761

    temp = mStation(name="霍尼韦尔", time=datetime.strptime(arrCompTime, '%H:%M').time(),
                     dirtocompany=True, lat=lat, lon=lon, campus=arrCampus)
    returnrec.append(temp.to_json())
    temp = mStation(name="霍尼韦尔", time=datetime.strptime(LeaveComTime, '%H:%M').time(),
                     dirtocompany=False, lat=lat, lon=lon, campus=arrCampus)
    returnrec.append(temp.to_json())
    '''

    #sort by time before response
    returnrec = sorted(returnrec, key=lambda x: x['time'])
    return jsonify(returnrec)

