from . import api
from .. models import Bus, Station, User, Post
from .. models import mBus, mStation, mUser, DiagramData
from flask import request, jsonify
from .. import db
from .authentication import auth

@api.route('/ebusdata/bus/', methods=['POST'])
def post_businfo():
    bus = Bus.from_json(request.json)
    busrec = Bus.query.filter_by(ebus_id=bus.ebus_id).first()
    if busrec is not None:
        busrec.ebus_id = bus.ebus_id
        busrec.name = bus.name
        busrec.cz_name = bus.cz_name
        busrec.cz_phone = bus.cz_phone
        busrec.sj_name = bus.sj_name
        busrec.sj_phone = bus.sj_phone
        busrec.seat_num = bus.seat_num
    else:
        busrec = bus
    db.session.add(busrec)
    db.session.commit()
    return jsonify(busrec.to_json())



@api.route('/ebusdata/station/', methods=['POST'])
def post_stationinfo():
    station = Station.from_json(request.json)
    stationrec = Station.query.filter_by(ebus_id=station.ebus_id).first()
    if stationrec is not None:
        stationrec.ebus_id = station.ebus_id
        stationrec.name = station.name
        stationrec.description = station.description
        stationrec.time = station.time
        stationrec.dirtocompany = station.dirtocompany
        stationrec.lat = station.lat
        stationrec.lon = station.lon
        stationrec.bus_id_fromebus = station.bus_id_fromebus
    else:
        stationrec = station
    db.session.add(stationrec)
    db.session.commit()
    return jsonify(stationrec.to_json())


@api.route('/ebusdata/endpost/')
def post_end_handle():
    #join station table to ebusdata table
    qresult = Station.query.all()
    for item in qresult:
        bus = Bus.query.filter_by(ebus_id=item.bus_id_fromebus).first()
        if bus is not None:
            item.bus = bus
        db.session.add(item)
        db.session.commit()
    qresultbus = Bus.query.all()
    return jsonify({'all stations in database:' : [item2.to_json() for item2 in qresult],
                    'all bus in database: ' : [item3.to_json() for item3 in qresultbus]})


@api.route('/getdata/')
def get_test_data():
    try:
        users = User.query.all()
        posts = Post.query.all()
        return jsonify({'all users: ': [item.to_json() for item in users],
                        'all posts: ': [item2.to_json() for item2 in posts]})
    except Exception as e:
        users = None
        posts = None
        return jsonify({'Oops! Something wrong!':'%s' %e })



