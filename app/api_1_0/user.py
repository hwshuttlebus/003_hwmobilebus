from flask import jsonify, request, url_for, current_app
from flask_login import current_user, login_required
from . import api
from .. models import mBus, mStation, mUser, mPost, db, Message


@api.route('/mbusdata/getregbus/')
def getregbus():
    tocompstation = None
    tohomestation = None
    tocompbus = None
    tohomebus = None
    stations = current_user.stations.all()
    if stations is not None:
        for station in stations:
            #get stations
            if station.dirtocompany == True:
                tocompstation = station
                #get bus
                userrec = mUser.query.filter_by(id=station.bus_id).first()
                if userrec is not None:
                    tocompbus = userrec
            else:
                tohomestation = station
                #get bus
                userrec = mUser.query.filter_by(id=station.bus_id).first()
                if userrec is not None:
                    tohomebus = userrec
            
    if tocompstation is not None and tohomestation is not None \
        and tocompbus is not None and tohomebus is not None:
        return jsonify({'tocompbus': tocompbus.to_json(),
                        'tocompstation': tocompstation.to_json(),
                        'tohomebus': tohomebus.to_json(),
                        'tohomestation': tohomestation.to_json()})
    else:
        return jsonify({'tocompbus': '',
                        'tocompstation': '',
                        'tohomebus': '',
                        'tohomestation': ''})

@api.route('/mbusdata/applystation/', methods=['POST'])
def applystation():
    try:
        jsonres = request.get_json()
    except Exception as e:
        return jsonify({'ERROR!':'%s' %e })

    if jsonres is not None:
        desc = jsonres.get('station_desc')
        lng = jsonres.get('station_lng')
        lat = jsonres.get('station_lat')
        userrec = mUser.query.filter_by(id=current_user.id).first()
        if userrec is not None:
            userrec.applyflag = True
            userrec.applydesc = desc
            userrec.lon = lng
            userrec.lat = lat
            db.session.add(userrec)
            db.session.commit()
            return jsonify(userrec.to_json())

@api.route('/mbusdata/postregbus/', methods=['POST'])
def post_regbus():
    userrec = mUser.query.filter_by(id=current_user.id).first()

    tocompid = request.json.get('tocompid')
    if tocompid is not None:
        stationrec1 = mStation.query.filter_by(id=tocompid).first()
        if stationrec1 is None:
            return jsonify({'user register fail:':'Invalid to company station information!'})

    tohomeid = request.json.get('tohomeid')
    if tohomeid is not None:
        stationrec2 = mStation.query.filter_by(id=tohomeid).first()
        if stationrec2 is None:
            return jsonify({'user register fail:':'Invalid to home station information!'})

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


@api.route('/mbusdata/curruser/')
@login_required
def getcurruser():
    return jsonify(current_user.to_json())

@api.route('/mbusdata/users/<int:id>')
def get_user(id):
    user = mUser.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/mbusdata/users/<int:id>/posts/')
def get_user_posts(id):
    user = mUser.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(mPost.timestamp.desc()).paginate(
        page, per_page=current_app.config['MBUS_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page-1,
                        _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page+1,
                        _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api.route('/mbusdata/getallposts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = mPost.query.paginate(
        page, per_page=current_app.config['MBUS_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'prevpage': (page-1),
        'nextpage': (page+1),
        'count': pagination.total,
        'perpage': pagination.per_page
    })

@api.route('/mbusdata/posts/', methods=['POST'])
def new_post():
    post = mPost.from_json(request.json)
    post.author = current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id, _external=True)}

@api.route('/mbusdata/posts/<int:id>')
def get_post(id):
    post = mPost.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/mbusdata/delposts/<int:id>', methods=['POST'])
def del_post(id):
    post = mPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'DELETED post': post.to_json()})

@api.route('/mbusdata/messages/', methods=['POST'])
def new_message():
    msg = Message.from_json(request.json)
    db.session.add(msg)
    db.session.commit()
    return jsonify(msg.to_json())

@api.route('/mbusdata/getallmessages/')
def get_message():
    msgs = Message.query.all()
    return jsonify({'Message': [msg.to_json() for msg in msgs]})

@api.route('/mbusdata/delmessages/<int:id>', methods=['POST'])
def del_msg(id):
    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'DELETED msg': msg.to_json()})