from . import api
from .. import db
from ..models import mBus, mStation, mUser
from flask import request, jsonify
from .authentication import auth

@api.route('/mbusdata/gpsdata/', methods=['POST'])
@auth.login_required
def post_gpsdata():
    try:
        busrec = mBus.update_gps(request.json)
    except Exception as e:
        return jsonify({'ERROR!':'%s' %e })

    if busrec is not None:
        #update or create item to database
        db.session.add(busrec)
        db.session.commit()
        return jsonify(busrec.to_json())
    else:
        return jsonify({'ERROR!': 'no such equipment id'})

    

