from . import api
from flask import jsonify, request
from datetime import datetime
from .authentication import auth
from .. models import db, mStation, mBus


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
    db.session.commit()

    for item2 in stationrec1:
        db.session.add(item2)
    for item3 in stationrec2:
        db.session.add(item3)
    db.session.commit()

    return jsonify({'added bus record: ': busrec.to_json(), 
                    'added station1 record: ': [item.to_json() for item in stationrec1],
                    'added station2 record: ': [item.to_json() for item in stationrec2]})


@api.route('/mbusdata/BusStation/bus/<int:id>', methods=['GET'])
def get_bus(id):
    busrec = mBus.query.filter_by(id=id).first()
    if busrec is not None:
        return jsonify(busrec.to_json())
    else:
        return jsonify({'ERROR': 'No such bus data'})


@api.route('/mbusdata/BusStation/bus/delete/<int:id>', methods=['POST'])
def delete_bus(id):
    busrec = mBus.query.filter_by(id=id).first()
    if busrec is not None:
        db.session.delete(busrec)
        db.session.commit()
    return jsonify({'deleted bus:': busrec.to_json()})

@api.route('/mbusdata/BusStation/station/delete/<int:id>',methods=['POST'])
def delete_station(id):
    stationrec = mStation.query.get_or_404(id=id)
    db.session.delete(stationrec)
    db.session.commit()
    return jsonify({'deleted station:' : stationrec.to_json()})


@api.route('/mbusdata/bus/<int:id>/stations')
def get_bus_related_stations(id):
    busrec = mBus.query.get_or_404(id)
    stationrecs = busrec.stations
    returnrec = []
    for stationrec in stationrecs:
        returnrec.append(stationrec.to_json())

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

    #sort by time before response
    returnrec = sorted(returnrec, key=lambda x: x['time'])
    return jsonify(returnrec)
