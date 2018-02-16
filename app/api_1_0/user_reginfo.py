from flask import jsonify, request
from . import api
from .. models import mBus, mStation, mUser, db


@api.route('/mbusdata/userreg/', methods=['POST'])
def post_userreginfo():
    user = mUser.from_json(request.json)
    userrec = mUser.query.filter_by(name=user.name).first()

    station_tocompany = request.json.get('station_tocompany')
    if station_tocompany is not None:
        station = mStation.from_json(request.json, True)
        stationrec1 = mStation.query.filter_by(name=station.name, dirtocompany=station.dirtocompany).first()
        if stationrec1 is None:
            return jsonify({'user register fail:':'Invalid to company station information!'})

    station_tohome = request.json.get('station_tohome')
    if station_tohome is not None:
        station = mStation.from_json(request.json, False)
        stationrec2 = mStation.query.filter_by(name=station.name, dirtocompany=station.dirtocompany).first()
        if stationrec2 is None:
            return jsonify({'user register fail:':'Invalid to home station information!'})

    if userrec is not None:
        userrec.mailaddr = user.mailaddr
    else:
        userrec = user

    if (userrec.is_reg_station(stationrec1) == False) or (userrec.is_reg_station(stationrec2) == False):
        #clear all the station record stored previously
        allstations = userrec.stations.all()
        for item in allstations:
            userrec.stations.remove(item)
        #update latest
        userrec.stations.append(stationrec1)
        userrec.stations.append(stationrec2)

    db.session.add(userrec)
    db.session.commit()
    return jsonify(userrec.to_json())
