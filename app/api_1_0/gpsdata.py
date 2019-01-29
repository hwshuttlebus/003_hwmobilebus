from . import api
from .. import db
from ..models import mBus, mStation, mUser
from flask import request, jsonify, current_app
from .authentication import auth

import time

@api.route('/mbusdata/gpsconfig/', methods=['GET'])
def configgps():
    retjson = {
        'toworkstart': current_app.config['MBUS_GPS_TOCOMPANYSTART'],
        'toworkend': current_app.config['MBUS_GPS_TOCOMPANYEND'],
        'tohomestart': current_app.config['MBUS_GPS_TOHOMESTART'],
        'tohomeend': current_app.config['MBUS_GPS_TOHOMEEND']
    }
    return jsonify(retjson)

@api.route('/mbusdata/gpsdata/', methods=['POST'])
#@auth.login_required
def post_gpsdata():
    nowtimetk1 = time.time()

    busrec = None
    try:
        #ignore mimetype check for GPS hardware
        jsonres = request.get_json(force=True)
    except Exception as e:
        print('!!!!!!!raw data!!!!!!!!!')
        print(request.get_data())
        print('%s' %e )
        return jsonify({'ERROR!':'%s' %e })

    if jsonres is not None:
        #try:
        busrec = mBus.update_gps(jsonres)
        #except Exception as e:
        #    return jsonify({'ERROR!':'%s' %e })

    if busrec is not None:
        #update or create item to database
        db.session.add(busrec)
        db.session.commit()
        nowtimetk2 = time.time()
        print('!!!Completed to handle a GPS signal: handle time={}, bus_number={}'.format(nowtimetk2-nowtimetk1, busrec.number))
        return jsonify(busrec.to_json())
    else:
        return jsonify({'ERROR!': 'no such equipment id or gps data is incorrect'})
