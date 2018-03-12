from . import db
from . import login_manager
from datetime import datetime
from .exceptions import ValidationError
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from math import radians, cos, sin, asin, sqrt
from dateutil import tz
import time

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r * 1000 # meters for unit

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
    number = db.Column(db.Integer, default=0)
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

    #client location data
    curridx = db.Column(db.Integer, default=0xFF)
    lefttime = db.Column(db.Integer, default=0)
    abntime = db.Column(db.Integer,default=0)

    #interface for restapi use
    def to_json(self):
        if self.recordtime is not None:
            recordtimestr = self.recordtime.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            recordtimestr = 'None'
        json_post = {
            'id': self.id,
            'name': self.name,
            'number': self.number,
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
            'currindx': self.curridx,
            'lefttime': self.lefttime,
            'abntime': self.abntime,
            'stations': url_for('api.get_bus_related_stations', id=self.id, _external=True)
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        name = json_post.get('bus_name')
        number = json_post.get('bus_number')
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
                    color=color, buslicense=buslicense, campus=campus, number=number)

    @staticmethod
    def locCoreAlgorithm(currentidx, lefttime, busrec, station, lon, lat):
        nowtimetk = time.time()

        print('!!!current location: '+str(lon)+', '+str(lat))
        if currentidx <= (len(station)-2):
            print('!!!station[currentidx+1].lon, station[currentidx+1].lat:'+str(station[currentidx+1].lon)+', '+str(station[currentidx+1].lat))
        averagespeed = 15#about 60km/h bus average speed
        if busrec.abntime is None:
            abntime = 0
        else:
            abntime = busrec.abntime

        if currentidx <= (len(station)-2):
            leftdist = haversine(lon, lat, station[currentidx+1].lon, station[currentidx+1].lat)
            lefttime = (leftdist*1.5/averagespeed)/60 # unit-->minute
            print('!!!leftdist and lefttime:'+str(leftdist)+',  '+str(lefttime))
            #if current leftdistance greater than 3000 meters and current lefttime greater than last lefttime
            #regard it for mistake calculated for currentindex
            if (leftdist > 3000) and (busrec.lefttime < lefttime):
                #abnormal case
                #handle based on abnormal time.
                if abntime == 0:
                    #the first time abnormal only record time tick
                    abntime = nowtimetk
                else:
                    if (nowtimetk - abntime) >= 30:
                        #during 30 seconds, the bus is always far from dest station
                        ##recalculate the current station once
                        abntime = nowtimetk
                        currentidx = mBus.getnearstation(station, lon, lat)
                        print('!!!recalculate the current station once index:'+str(currentidx))
                        if currentidx <= (len(station)-2):
                            leftdist = haversine(lon, lat, station[currentidx+1].lon, station[currentidx+1].lat)
                            lefttime = (leftdist/averagespeed)/60
                            print('!!!leftdist and lefttime:'+str(leftdist)+',  '+str(lefttime))
            else:
                #normal case
                #if in abnormal case before, regard enter normal state when following condition meet:
                #   during 10 seconds the bus location is near to dest station
                print('!!!!!!!!!!!!!!!!!!!!')
                print(nowtimetk)
                print(abntime)
                if ((nowtimetk-abntime)<=10) and (abntime!=0):
                    print('!!! re-enter normal state')
                    abntime = 0
                if leftdist <= 30.0:
                    #arrived and index to next station
                    currentidx = currentidx+1      
                    print('!!!#arrived and index to next station index:　'+str(currentidx))
                    if currentidx <= (len(station)-2):
                        leftdist = haversine(lon, lat, station[currentidx+1].lon, station[currentidx+1].lat)
                        lefttime = (leftdist*1.5/averagespeed)/60 # unit-->minute

        return currentidx, lefttime, abntime
    
    @staticmethod
    def getnearstation(stations, lon, lat):
        #iterate stations
        for idx, item in enumerate(stations):
            distnew = haversine(item.lon, item.lat, lon, lat)
            if idx == 0:
                distold = distnew
                retindex = 0
            elif distnew < distold:
                retindex = idx
                distold = distnew
        return retindex

    @staticmethod
    def calbuslocation(busrec, lon, lat):
        #init variable
        currentidx = 0xFF       
        lefttime = 0
        abntime = 0
        
        

        stations = busrec.stations.order_by(mStation.time).all()
        #get current Beijing time
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Aisa/Shanghai')

        #utcnowtime= datetime.utcnow()
        #utcnowtime = utcnowtime.replace(tzinfo=from_zone)
        #nowtime = utcnowtime.astimezone(to_zone)

        utcnowtime = datetime.strptime('2018-03-08T07:35:21', '%Y-%m-%dT%H:%M:%S')
        nowtime = utcnowtime

        #define string const for time
        towkstart = "06:30:00"
        towkend = "10:00:00"
        tohmstart = "16:55:00"
        tohmend = "20:00:00"

        #transfer to datetime object
        strprefix = nowtime.strftime('%Y-%m-%dT')

        towkstartobj = datetime.strptime(strprefix+towkstart, '%Y-%m-%dT%H:%M:%S')
        towkendobj = datetime.strptime(strprefix+towkend, '%Y-%m-%dT%H:%M:%S')
        tohmstartobj = datetime.strptime(strprefix+tohmstart, '%Y-%m-%dT%H:%M:%S')
        tohmendobj = datetime.strptime(strprefix+tohmend, '%Y-%m-%dT%H:%M:%S')

        print(nowtime)
        nowtime = nowtime.replace(tzinfo=None)
        
        print(towkstartobj)
        print(towkendobj)
        print(tohmstartobj)
        print(tohmendobj)
        print(nowtime)

        #judge whether in work time and filter related station
        stationup = []
        stationdown = []
        for item in stations:
            if (True == item.dirtocompany):
                stationup.append(item)
            else:
                stationdown.append(item)
        #ENTER CORE ASSESSMENT ALGUORITHM 
        if (((nowtime >= towkstartobj) and (nowtime <= towkendobj)) or
             ((nowtime >= tohmstartobj) and (nowtime <= tohmendobj))):

             
            if ((nowtime >= towkstartobj) and (nowtime <= towkendobj)):
                print('!!!enter to company procedure')
                station = stationup
            else:
                print('!!!enter to home procedure')
                station = stationdown

            if (busrec.curridx == 0xFF) and ((busrec.recordtime < towkstartobj) or (busrec.recordtime < tohmstartobj)):
                #first time recv valid gps data after enter shuttle bus time
                if nowtime.time() <= station[0].time:
                    #GPS data recv before arrive at first stop
                    currentidx = -1
                    print('!!!GPS data recv before arrive at first stop')
                    currentidx, lefttime, abntime = mBus.locCoreAlgorithm(currentidx, lefttime, busrec, station, lon, lat)
                else:
                    #GPS data recv after the first stop
                    #should find the nearest station index for current bus location
                    currentidx = mBus.getnearstation(station, lon, lat)
                    print('!!!GPS data recv after the first stop latest index is:' +str(currentidx))
            else:
                #already recv valid gps data after enter shuttle bus time
                #re-calculate the left distance and left time
                currentidx = busrec.curridx
                print('!!!re-calculate the left distance and left time current idex:'+str(currentidx))
                currentidx, lefttime, abntime = mBus.locCoreAlgorithm(currentidx, lefttime, busrec, station, lon, lat)

        else:
            #not in shuttle bus time, return invalid data
            print('!!!not in shuttle bus time, return invalid data')
          
        return currentidx, lefttime, abntime

    @staticmethod
    def update_gps(json_post):
        #parse json data
        equip_id = json_post.get('bus_equip_id')
        lat = json_post.get('bus_lat')
        lon = json_post.get('bus_lon')
        recordtime = json_post.get('bus_recordtime')
        if recordtime is not None:
            datetimeobj = datetime.strptime(recordtime.strip(), '%Y-%m-%dT%H:%M:%S')
        else:
            datetimeobj = datetime.strptime('2000-01-01T12:12:12', '%Y-%m-%dT%H:%M:%S')

        #update
        busrec = mBus.query.filter_by(equip_id=equip_id).first()
        if busrec is not None:
            #first update location
            busrec.curridx, busrec.lefttime, busrec.abntime = mBus.calbuslocation(busrec, lon, lat)
            #next update json data
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
        name = json_post.get('name')
        description = json_post.get('description')
        time = json_post.get('time')
        if time is not None:
            datetimeobj = datetime.strptime(time.strip(), '%H:%M').time()
        else:
            datetimeobj = datetime.strptime('7:30', '%H:%M').time()
        lat = json_post.get('lat')
        lon = json_post.get('lon')
        campus = json_post.get('campus')
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









