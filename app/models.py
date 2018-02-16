from . import db
from . import login_manager
from datetime import datetime
from .exceptions import ValidationError
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for

class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    ebus_id = db.Column(db.Integer, unique=True, index=True)
    name = db.Column(db.String(64))
    cz_name = db.Column(db.String(64), default="")
    cz_phone = db.Column(db.String(30), default="")
    sj_name = db.Column(db.String(64), default="")
    sj_phone = db.Column(db.String(64), default="")
    seat_num = db.Column(db.Integer, default=0)
    stations = db.relationship('Station', backref='bus', lazy='dynamic')

    def to_json(self):
        json_post = {
            'id': self.id,
            'ebus_id': self.ebus_id,
            'name': self.name,
            'cz_name': self.cz_name,
            'cz_phone': self.cz_phone,
            'sj_name': self.sj_name,
            'sj_phone': self.sj_phone,
            'seat_num': self.seat_num
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        ebus_id = json_post.get('ebus_id')
        name = json_post.get('name')
        cz_name = json_post.get('cz_name')
        cz_phone = json_post.get('cz_phone')
        sj_name = json_post.get('sj_name')
        sj_phone = json_post.get('sj_phone')
        seat_num = json_post.get('seat_num')
        if ebus_id is None:
            raise ValidationError('ebusdata import fail: id in ebus not exists!')
        return Bus(ebus_id=ebus_id, name=name, cz_name=cz_name, cz_phone=cz_phone,
                   sj_name=sj_name, sj_phone=sj_phone, seat_num=seat_num)

class Station(db.Model):
    __tablename__ = 'stations'
    id = db.Column(db.Integer, primary_key=True)
    ebus_id = db.Column(db.Integer, unique=True, index=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text(), default="")
    time = db.Column(db.Time())
    dirtocompany = db.Column(db.Boolean(), default=False)
    lat = db.Column(db.Float(precision='11,8'), default=0)
    lon = db.Column(db.Float(precision='11,8'), default=0)
    bus_id_fromebus = db.Column(db.Integer)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'))

    def to_json(self):
        json_post = {
            'id': self.id,
            'ebus_id': self.ebus_id,
            'name': self.name,
            'description': self.description,
            'time': self.time.strftime('%H:%M'),
            'dirtocompany': self.dirtocompany,
            'lat': self.lat,
            'lon': self.lon,
            'bus_id_fromebus': self.bus_id_fromebus,
            'bus_id': self.bus_id
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        ebus_id = json_post.get('ebus_id')
        name = json_post.get('name')
        description = json_post.get('description')
        time = json_post.get('time')
        if time is not None:
            datetimeobj = datetime.strptime(time.strip(), '%H:%M').time()
        else:
            datetimeobj = datetime.strptime('7:30', '%H:%M').time()
        dirtocompany = json_post.get('dirtocompany')
        lat = json_post.get('lat')
        lon = json_post.get('lon')
        bus_id_fromebus = json_post.get('bus_id_fromebus')
        if ebus_id is None or bus_id_fromebus is None:
            raise ValidationError('ebusdata import fail! id or id_fromebus in station not exists!')
        return Station(ebus_id=ebus_id, name=name, description=description, time=datetimeobj,
                       bus_id_fromebus=bus_id_fromebus,dirtocompany=dirtocompany, lat=lat, lon=lon)


#following models is setup for access remote pre-existing cardevent related database
class User(UserMixin, db.Model):
    __bind_key__ = 'tests'
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    username = db.Column(db.String)

    def to_json(self):
        json_post = {
            'id' : self.id,
            'email': self.email,
            'username': self.username
        }
        return json_post

class Post(db.Model):
    __bind_key__ = 'tests'
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    authorid = db.Column(db.Integer, db.ForeignKey('users.id'))


    def to_json(self):
        json_post = {
            'id' : self.id,
            'body': self.body,
            'authorid': self.authorid
        }
        return json_post

#following Model is for formal mbus use
class mBus(db.Model):
    __tablename__ = 'mbuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    cz_name = db.Column(db.String(64), default="")
    cz_phone = db.Column(db.String(30), default="")
    sj_name = db.Column(db.String(64), default="")
    sj_phone = db.Column(db.String(64), default="")
    seat_num = db.Column(db.String(64), default="")
    color = db.Column(db.String(64), default="")
    buslicense = db.Column(db.String(64), default="")
    campus = db.Column(db.String(64), default="")
    stations = db.relationship('mStation', backref='mbus', lazy='dynamic',cascade='all, delete-orphan')

    #GPS data for specific bus
    equip_id = db.Column(db.Integer, default=0)
    lat = db.Column(db.Float(precision='11,8'), default=0)
    lon = db.Column(db.Float(precision='11,8'), default=0)
    recordtime = db.Column(db.DateTime())

    #interface for restapi use
    def to_json(self):
        if self.recordtime is not None:
            recordtimestr = self.recordtime.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            recordtimestr = 'None'
        json_post = {
            'id': self.id,
            'name': self.name,
            'cz_name': self.cz_name,
            'cz_phone': self.cz_phone,
            'sj_name': self.sj_name,
            'sj_phone': self.sj_phone,
            'seat_num': self.seat_num,
            'equip_id': self.equip_id,
            'lat': self.lat,
            'lon': self.lon,
            'recordtime': recordtimestr,
            'color': self.color,
            'buslicense': self.buslicense,
            'campus': self.campus,
            'stations': url_for('api.get_bus_related_stations', id=self.id, _external=True)
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        name = json_post.get('bus_name')
        cz_name = json_post.get('bus_cz_name')
        cz_phone = json_post.get('bus_cz_phone')
        sj_name = json_post.get('bus_sj_name')
        sj_phone = json_post.get('bus_sj_phone')
        seat_num = json_post.get('bus_seat_num')
        equip_id = json_post.get('bus_equip_id')
        color = json_post.get('bus_color')
        buslicense = json_post.get('bus_buslicense')
        campus = json_post.get('bus_campus')
 
        return mBus(name=name, cz_name=cz_name, cz_phone=cz_phone,sj_name=sj_name, 
                    sj_phone=sj_phone, seat_num=seat_num, equip_id=equip_id,
                    color=color, buslicense=buslicense, campus=campus)

    @staticmethod
    def update_gps(json_post):
        equip_id = json_post.get('bus_equip_id')
        lat = json_post.get('bus_lat')
        lon = json_post.get('bus_lon')
        recordtime = json_post.get('bus_recordtime')
        if recordtime is not None:
            datetimeobj = datetime.strptime(recordtime.strip(), '%Y-%m-%dT%H:%M:%S')
        else:
            datetimeobj = datetime.strptime('2000-01-01T12:12:12', '%Y-%m-%dT%H:%M:%S')

        busrec = mBus.query.filter_by(equip_id=equip_id).first()
        if busrec is not None:
            #update
            busrec.equip_id = equip_id
            busrec.lat = lat
            busrec.lon = lon
            busrec.recordtime = datetimeobj
            return busrec
        else:
            return None

class mStation(db.Model):
    __tablename__ = 'mstations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text(), default="")
    time = db.Column(db.Time())
    dirtocompany = db.Column(db.Boolean(), default=False)
    lat = db.Column(db.Float(precision='11,8'), default=0)
    lon = db.Column(db.Float(precision='11,8'), default=0)
    campus = db.Column(db.String(64), default="")
    bus_id = db.Column(db.Integer, db.ForeignKey('mbuses.id'))
    diagrams = db.relationship('DiagramData', backref='mstation', lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_json(self):
        json_post = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'time': self.time.strftime('%H:%M'),
            'dirtocompany': self.dirtocompany,
            'lat': self.lat,
            'lon': self.lon,
            'bus_id': self.bus_id,
            'campus': self.campus
        }
        return json_post

    @staticmethod
    def from_json(json_post, isdirtocompany):
        name = json_post.get('station_name')
        description = json_post.get('station_description')
        time = json_post.get('station_time')
        if time is not None:
            datetimeobj = datetime.strptime(time.strip(), '%H:%M').time()
        else:
            datetimeobj = datetime.strptime('7:30', '%H:%M').time()
        lat = json_post.get('station_lat')
        lon = json_post.get('station_lon')
        campus = json_post.get('station_campus')
        return mStation(name=name, description=description, time=datetimeobj,
                       dirtocompany=isdirtocompany, lat=lat, lon=lon, campus=campus)


registrations = db.Table('registration',
    db.Column('user_id', db.Integer, db.ForeignKey('musers.id')),
    db.Column('station_id', db.Integer, db.ForeignKey('mstations.id'))
)


class mRole(db.Model):
    __tablename__ = 'mroles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=True, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('mUser', backref='mrole', lazy='dynamic')


class mUser(UserMixin, db.Model):
    __tablename__ = 'musers'
    id = db.Column(db.Integer, primary_key=True)
    mailaddr = db.Column(db.String(64), default="")
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('mroles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('mPost', backref='author', lazy='dynamic')
    stations = db.relationship('mStation',
                               secondary=registrations,
                               backref=db.backref('muser', lazy='dynamic'),
                               lazy='dynamic')

    #reserved for future use
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True   

    def is_reg_station(self, station):
        return self.stations.filter_by(id=station.id).first() is not None

    def to_json(self):
        json_post = {
            'id' : self.id,
            'mailaddr' : self.mailaddr,
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        mailaddr = json_post.get('mailaddr')
        return mUser(mailaddr=mailaddr)

class mPost(db.Model):
    __tablename__ = 'mposts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('musers.id'))
    body_html = db.Column(db.Text)

class DiagramData(db.Model):
    __tablename__ = 'diagrams'
    id = db.Column(db.Integer, primary_key=True)
    mdate = db.Column(db.Time())
    arrive_time = db.Column(db.Time())
    current_num = db.Column(db.Integer, default=0)
    station_id = db.Column(db.Integer, db.ForeignKey('mstations.id'))

    def to_json(self):
        json_post = {
            'id': self.id,
            'mdate': self.time.strftime('%Y-%m-%d'),
            'arrive_time': self.time.strftime('%H:%M'),
            'current_num': self.current_num,
            'station_id': self.station_id
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        if mdate is not None:
            mdateobj = datetime.strptime(time.strip(), '%Y-%m-%d').time()
        else:
            mdateobj = datetime.strptime('2000-01-01', '%Y-%m-%d').time()

        if arrive_time is not None:
            arrive_timeobj = datetime.strptime(time.strip(), '%H:%M').time()
        else:
            arrive_timeobj = datetime.strptime('00:00', '%H:%M').time()

        current_num = json_post.get('current_num')
        station_id = json_post.get('station_id')
        return DiagramData(mdate=mdate, mdateobj=mdateobj, arrive_timeobj=arrive_timeobj,
                           current_num=current_num)


@login_manager.user_loader
def load_user(user_id):
    return mUser.query.get(int(user_id))









