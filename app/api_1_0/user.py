from flask import jsonify, request, url_for, current_app
from flask_login import current_user
from . import api
from .. models import mBus, mStation, mUser, mPost, db

'''
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
'''

@api.route('/mbusdata/curruser/')
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