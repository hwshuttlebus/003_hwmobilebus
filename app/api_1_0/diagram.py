from flask import jsonify, request, current_app, url_for
from . import api
from .. models import DiagramData, db, BusDiagramData, get_currbj_time
from datetime import timedelta

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