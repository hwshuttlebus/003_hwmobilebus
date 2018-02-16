from flask import jsonify, request
from . import api
from .. models import DiagramData, db


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

    station = mStation.query.filter_by(id=diatram.station_id).first()
    if station is not None:
        diagramrec.mstation = station
    else:
        return jsonify({'invalid mstation id: ' : 'ERROR'})

    db.session.add(diagramrec)
    db.session.commit()
    return jsonify(diagramrec.to_json())