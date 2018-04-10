from . import db
from . import login_manager
from datetime import datetime, timedelta
from .exceptions import ValidationError
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from math import radians, cos, sin, asin, sqrt
from dateutil import tz
import time
from .gpsutil import wgs84togcj02, gcj02tobd09
from . import celery
from config import Config

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

def get_currbj_time():
    

    #get current Beijing time
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Shanghai')
    utcnowtime= datetime.utcnow()
    utcnowtime = utcnowtime.replace(tzinfo=from_zone)
    nowtime = utcnowtime.astimezone(to_zone)

    #utcnowtime = datetime.strptime('2018-04-03T07:35:21', '%Y-%m-%dT%H:%M:%S')
    #nowtime = utcnowtime

    return nowtime


class Permission:
    COMMENT = 0x01
    ADMINISTER = 0X80


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
class Event(db.Model):
    __bind_key__ = 'buscard'
    __tablename__ = 'events'
    CarID = db.Column(db.String(20))
    DateTimes = db.Column(db.DateTime)
    CardNo = db.Column(db.String(20), primary_key=True)

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
    seat_num = db.Column(db.Integer, default=0)
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
    currdir = db.Column(db.Boolean(), default=False)
    lefttime = db.Column(db.Float(precision='11,7'), default=0)
    abntime = db.Column(db.Integer,default=0)
    abnleftDist = db.Column(db.Float(precision='11,7'), default=0)

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
            'currdir': self.currdir,
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
                    sj_phone=sj_phone, equip_id=equip_id,seat_num=seat_num,
                    color=color, buslicense=buslicense, campus=campus, number=number)
    
    
    @staticmethod
    def updatediagram(station, busrec):
        currbeijingtime = get_currbj_time()
        #update date
        mdateobj = currbeijingtime.date()
        #update time
        mtimeobj = currbeijingtime.time()
        #current number will update in celery task
        diagramrec = DiagramData(mdate=mdateobj, arrive_time=mtimeobj,current_num=0, station_id=station.id)
        print(diagramrec.to_json())
        db.session.add(diagramrec)
        db.session.commit()

    @staticmethod
    def fakediagram():
        currbeijingtime = get_currbj_time()
        #update date
        mdateobj = currbeijingtime.date()

        #in bus time
        timestr1 = [('07:28:10', 48),('07:45:01',49),('07:46:12',50), ('07:57:02', 51), ('08:04:00', 52), ('08:46:25', 53)]  
        timestr2 = [('17:42:10', 55),('17:51:01',56),('18:03:12',57)]  
        timestr1obj = []
        timestr2obj = []
        for item in timestr1:
            timestr1obj.append((datetime.strptime(item[0], '%H:%M:%S').time(), item[1]))
        for item2 in timestr2:
            timestr2obj.append((datetime.strptime(item2[0], '%H:%M:%S').time(), item2[1]))
        #duplicate
        timestr3 = [('07:40:01', 48),('07:45:03',50)]  
        timestr4 = [('18:08:12',57)]  
        timestr3obj = []
        timestr4obj = []
        for item in timestr3:
            timestr1obj.append((datetime.strptime(item[0], '%H:%M:%S').time(), item[1]))
        for item2 in timestr4:
            timestr2obj.append((datetime.strptime(item2[0], '%H:%M:%S').time(), item2[1]))

        for item3 in timestr1obj:
            diagramrec = DiagramData(mdate=mdateobj, arrive_time=item3[0],current_num=0, station_id=item3[1])
            db.session.add(diagramrec)
            db.session.commit()
        for item4 in timestr2obj:
            diagramrec = DiagramData(mdate=mdateobj, arrive_time=item4[0],current_num=0, station_id=item4[1])
            db.session.add(diagramrec)
            db.session.commit()

    @staticmethod
    def locCoreAlgorithm(currentidx, lefttime, busrec, station, lon, lat):
        nowtimetk = time.time()

        print('!!!current location: '+str(lon)+', '+str(lat))
        if currentidx <= (len(station)-2):
            print('!!!station[currentidx+1].lon, station[currentidx+1].lat:'+str(station[currentidx+1].lon)+', '+str(station[currentidx+1].lat))
        averagespeed = 15#about 60km/h bus average speed

        if busrec.abntime is None:
            abntime = 0.0
        else:
            abntime = busrec.abntime
        if busrec.abnleftDist is None:
            abnleftDist = 0.0
        else:
            abnleftDist = busrec.abnleftDist
        if busrec.lefttime is None:
            busreclefttime = 0.0
        else:
            busreclefttime = busrec.lefttime

        if currentidx <= (len(station)-2):
            leftdist = haversine(lon, lat, station[currentidx+1].lon, station[currentidx+1].lat)
            lefttime = (leftdist*1.5/averagespeed)/60 # unit-->minute
            print('!!!leftdist and lefttime:'+str(leftdist)+',  '+str(lefttime))
            print('!!!last leftime:'+str(busrec.lefttime))
            #if current lefttime greater than last lefttime
            #regard it for mistake calculated for currentindex
            if busreclefttime < lefttime:
                #abnormal case
                #handle based on abnormal time.
                if abntime == 0.0:
                    #the first time abnormal only record time tick and leftDistance
                    abntime = nowtimetk
                    abnleftDist = leftdist
                    print('!!!first time enter abnormal')
                    print('!!!abntime and abnleftDist:'+str(abntime)+', '+str(abnleftDist))
                else:
                    if ((nowtimetk - abntime) >= 30) and ((leftdist - abnleftDist) >= 200):
                        #during(more than) 30 seconds, the bus is always far from dest station
                        #with different distance more than 200 meters
                        ##recalculate the current station once
                        abntime = nowtimetk
                        abnleftDist = leftdist
                        currentidx = mBus.getnearstation(station, lon, lat)
                        mBus.updatediagram(station[currentidx], busrec)
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
                    abntime = 0.0
                    abnleftDist = 0.0
                if leftdist <= 100.0:
                    #arrived and index to next station
                    currentidx = currentidx+1      
                    print('!!!#arrived and index to next station index:　'+str(currentidx))
                    mBus.updatediagram(station[currentidx], busrec)
                    if currentidx <= (len(station)-2):
                        leftdist = haversine(lon, lat, station[currentidx+1].lon, station[currentidx+1].lat)
                        lefttime = (leftdist*1.5/averagespeed)/60 # unit-->minute

        return currentidx, lefttime, abntime, abnleftDist
    
    @staticmethod
    def getnearstation(stations, lon, lat):
        distold = 0
        distnew = 0
        retindex = 0
        #iterate stations
        for idx, item in enumerate(stations):
            if item.name is not None and item.lat is not None and item.lon is not None:
                distnew = haversine(item.lon, item.lat, lon, lat)
                if distold == 0:
                    distold = distnew
                    retindex = 0
                elif distnew < distold:
                    retindex = idx
                    distold = distnew
        return retindex

    @staticmethod
    def getnearsation_excomp(stations, lon, lat, direction):
        distold = 0
        distnew = 0
        #iterate stations, except for company
        for idx, item in enumerate(stations):
            if (item.name is not None) and (item.dirtocompany is not None) and \
                (not ("霍尼韦尔" in item.name)) and (item.dirtocompany == direction) and \
                item.lat is not None and item.lon is not None:
                distnew = haversine(item.lon, item.lat, lon, lat)
                if distold == 0:
                    distold = distnew
                    retindex = idx
                elif distnew < distold:
                    retindex = idx
                    distold = distnew

        return retindex, distold

    @staticmethod
    def calbuslocation(busrec, lon, lat, datetimeobj):
        #init variable
        currentidx = 0xFF
        currdir = False
        lefttime = 0
        abntime = 0
        abnleftDist = 0
        stationup = []
        stationdown = []
        
        #get the to company and to home stations
        stations = busrec.stations.order_by(mStation.time).all()
        for item in stations:
            if (True == item.dirtocompany):
                stationup.append(item)
            else:
                stationdown.append(item)

        #get current Beijing time
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Asia/Shanghai')

        utcnowtime= datetime.utcnow()
        utcnowtime = utcnowtime.replace(tzinfo=from_zone)
        nowtime = utcnowtime.astimezone(to_zone)

        #utcnowtime = datetime.strptime('2018-03-08T07:35:21', '%Y-%m-%dT%H:%M:%S')
        #nowtime = utcnowtime

        #define string const for time
        towkstart = stationup[0].time.strftime('%H:%M:%S')
        towkend = stationup[-1].time.strftime('%H:%M:%S')
        tohmstart = stationdown[0].time.strftime('%H:%M:%S')
        tohmend = stationdown[-1].time.strftime('%H:%M:%S')

        #transfer to datetime object
        strprefix = nowtime.strftime('%Y-%m-%dT')
        towkstartobj = datetime.strptime(strprefix+towkstart, '%Y-%m-%dT%H:%M:%S')
        towkendobj = datetime.strptime(strprefix+towkend, '%Y-%m-%dT%H:%M:%S')
        tohmstartobj = datetime.strptime(strprefix+tohmstart, '%Y-%m-%dT%H:%M:%S')
        tohmendobj = datetime.strptime(strprefix+tohmend, '%Y-%m-%dT%H:%M:%S')
        #add tolerance offset for time
        towkendoffsetobj = towkendobj + timedelta(minutes=60)
        tohmendoffsetobj = tohmendobj + timedelta(minutes=60)
        towkstartoffsetobj = towkstartobj - timedelta(minutes=10)
        tohmstartoffsetobj = tohmstartobj - timedelta(minutes=10)

        print('!!!!!! current time:')
        print(nowtime)
        nowtime = nowtime.replace(tzinfo=None)

        #ENTER CORE ASSESSMENT ALGUORITHM 
        if (((nowtime >= towkstartoffsetobj) and (nowtime <= towkendoffsetobj)) or
             ((nowtime >= tohmstartoffsetobj) and (nowtime <= tohmendoffsetobj))):
            print('!!! recv GPS data in shuttlebus time!')
            if ((nowtime >= towkstartoffsetobj) and (nowtime <= towkendoffsetobj)):
                if (datetimeobj >= towkstartoffsetobj) and (datetimeobj <= towkendoffsetobj):
                    print('!!!enter to company procedure')
                    station = stationup
                    currdir = True
                else:
                    print('!!!GPS time invalid! no valid data for to company time!')
                    #ignore this data, return data as before
                    return busrec.curridx, busrec.lefttime, busrec.abntime, busrec.abnleftDist, busrec.currdir
            else:
                if (datetimeobj >= tohmstartoffsetobj) and (datetimeobj <= tohmendoffsetobj):
                    print('!!!enter to home procedure')
                    station = stationdown
                    currdir = False
                else:
                    print('!!!GPS time invalid! no valid data for to home time!')
                    #ignore this data, return data as before
                    return busrec.curridx, busrec.lefttime, busrec.abntime, busrec.abnleftDist, busrec.currdir

            if busrec.curridx == 0xFF:
                #first time recv valid gps data after enter shuttle bus time
                if datetimeobj.time() <= station[0].time:
                    #GPS data recv before arrive at first stop
                    currentidx = -1
                    print('!!!GPS data recv before arrive at first stop')
                    currentidx, lefttime, abntime, abnleftDist = mBus.locCoreAlgorithm(currentidx, lefttime, busrec, station, lon, lat)
                else:
                    #GPS data recv after the first stop
                    #should find the nearest station index for current bus location
                    currentidx = mBus.getnearstation(station, lon, lat)
                    mBus.updatediagram(station[currentidx], busrec)
                    print('!!!GPS data recv after the first stop latest index is:' +str(currentidx))
            else:
                #already recv valid gps data after enter shuttle bus time
                #re-calculate the left distance and left time
                currentidx = busrec.curridx
                print('!!!re-calculate the left distance and left time current idex:'+str(currentidx))
                currentidx, lefttime, abntime, abnleftDist = mBus.locCoreAlgorithm(currentidx, lefttime, busrec, station, lon, lat)

        else:
            #not in shuttle bus time, return invalid data
            print('!!!not in shuttle bus time, return invalid data')
        
        return currentidx, lefttime, abntime, abnleftDist, currdir

    @staticmethod
    def update_gps(json_post):
        #parse json data
        equip_id = json_post.get('bus_equip_id')
        latwsg = json_post.get('bus_lat')
        lngwsg = json_post.get('bus_lon')

        #only for test use, transmit gps data from WSG84 to BD-09 
        lnggc02, latgc02 = wgs84togcj02(lngwsg, latwsg)
        lon, lat = gcj02tobd09(lnggc02, latgc02)

        recordtime = json_post.get('bus_recordtime')
        print('!!!current gps data: '+str(latwsg)+', '+str(lngwsg)+', '+ str(recordtime))

        if recordtime is not None:
            datetimeobj = datetime.strptime(recordtime.strip(), '%Y-%m-%dT%H:%M:%S')
        else:
            datetimeobj = datetime.strptime('2000-01-01T12:12:12', '%Y-%m-%dT%H:%M:%S')

        #update
        busrec = mBus.query.filter_by(equip_id=equip_id).first()
        if busrec is not None:
            #first update location
            busrec.curridx, busrec.lefttime, busrec.abntime, busrec.abnleftDist, busrec.currdir = mBus.calbuslocation(busrec, lon, lat, datetimeobj)
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
    users = db.relationship('mUser', backref='mrole', lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMENT, True),
            'Administrator': (Permission.ADMINISTER | Permission.COMMENT, False)
        }
        for r in roles:
            role = mRole.query.filter_by(name=r).first()
            if role is None:
                role = mRole(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class mUser(UserMixin, db.Model):
    __tablename__ = 'musers'
    id = db.Column(db.Integer, primary_key=True)
    mailaddr = db.Column(db.String(64), default="")
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('mroles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    campus = db.Column(db.String(64), default="")
    posts = db.relationship('mPost', backref='author', lazy='dynamic',cascade='all, delete-orphan')
    stations = db.relationship('mStation',
                               secondary=registrations,
                               backref=db.backref('muser', lazy='dynamic'),
                               lazy='dynamic')
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    
    #user applied station information
    applyflag = db.Column(db.Boolean, default=False)
    applydesc = db.Column(db.String(64), default="")
    lat = db.Column(db.Float(precision='11,8'), default=0)
    lon = db.Column(db.Float(precision='11,8'), default=0)

    #reserved for future use
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    avatar_hash = db.Column(db.String(32))

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = mUser(mailaddr=forgery_py.internet.email_address(),
                      name=forgery_py.internet.user_name(True),
                      password=forgery_py.lorem_ipsum.word(),
                      confirmed=True,
                      campus="libingroad",
                      member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def from_json(json_post):
        mailaddr = json_post.get('mailaddr')
        return mUser(mailaddr=mailaddr, campus=campus)

    def __init__(self, **kwargs):
        super(mUser, self).__init__(**kwargs)
        if self.mrole is None:
            if self.mailaddr == current_app.config['MBUS_ADMIN']:
                self.mrole = mRole.query.filter_by(permissions=0x81).first()
            if self.mrole is None:
                self.mrole = mRole.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_reset_token(self, expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

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

    def can(self, permissions):
        return self.mrole is not None and \
            (self.mrole.permissions & permissions) == permissions
    
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def is_reg_station(self, station):
        return self.stations.filter_by(id=station.id).first() is not None

    def to_json(self):
        json_post = {
            'id' : self.id,
            'mailaddr' : self.mailaddr,
            'campus': self.campus,
            'role_id': self.role_id,
            'role_name': self.mrole.name
        }
        return json_post

    

class mPost(db.Model):
    __tablename__ = 'mposts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('musers.id'))
    body_html = db.Column(db.Text)

    def to_json(self):
        json_post = {
            'id': self.id,
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html':self.body_html,
            'timestamp': self.timestamp.strftime('%Y-%m-%dT%H:%M:%S')+'+0000',
            'author_mailaddr': self.author.mailaddr,
            'author': url_for('main.user', mailaddr=self.author.mailaddr, _external=True)
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
             raise ValidationError('post does not have a body')
        return mPost(body=body)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = mUser.query.count()
        for i in range(count):
            u = mUser.query.offset(randint(0, user_count-1)).first()
            p = mPost(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                      timestamp=forgery_py.date.date(True),
                      author=u)
            db.session.add(p)
            db.session.commit()


class AnoymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnoymousUser


@login_manager.user_loader
def load_user(userid):
    return mUser.query.get(int(userid))



class BusDiagramData(db.Model):
    __tablename__ = 'busdiagrams'
    id = db.Column(db.Integer, primary_key=True)
    mdate = db.Column(db.Date())
    arrive_time = db.Column(db.Time())
    tocomp_num = db.Column(db.Integer, default=0)
    tohome_num = db.Column(db.Integer, default=0)
    bus_id = db.Column(db.Integer, default=0)

    def to_json(self):
        json_post = None
        stationup = []

        busrec = mBus.query.filter_by(id=self.bus_id).first()
        if busrec is not None:
            stations = busrec.stations.order_by(mStation.time).all()
            for item in stations:
                if True == item.dirtocompany:
                    stationup.append(item)
            bustime = stationup[-1].time
            if busrec.seat_num is None:
                totalnumber = 0
            else:
                totalnumber = busrec.seat_num 
            if bustime is not None:
                json_post = {
                    'bid': self.bus_id,
                    'daytime': self.mdate.strftime('%Y-%m-%d'),
                    'tocomp_num': self.tocomp_num,
                    'tohome_num': self.tohome_num,
                    'arriveTime': self.arrive_time.strftime('%H:%M:%S'),
                    'totalNum': totalnumber,
                    'busTime': bustime.strftime('%H:%M:%S')
            }

        return json_post


class DiagramData(db.Model):
    __tablename__ = 'diagrams'
    id = db.Column(db.Integer, primary_key=True)
    mdate = db.Column(db.Date())
    arrive_time = db.Column(db.Time())
    current_num = db.Column(db.Integer, default=0)
    station_id = db.Column(db.Integer, db.ForeignKey('mstations.id'))


    def to_json(self):
        json_post = None
        stationrec  = mStation.query.filter_by(id=self.station_id).first()
        if stationrec is not None:
            bustime = stationrec.time
            if stationrec.mbus.seat_num is None:
                totalnumber = 0
            else:
                totalnumber = stationrec.mbus.seat_num 
            if bustime is not None:
                json_post = {
                    'sid': self.station_id,
                    'daytime': self.mdate.strftime('%Y-%m-%d'),
                    'currentNum': self.current_num,
                    'arriveTime': self.arrive_time.strftime('%H:%M:%S'),
                    'totalNum': totalnumber,
                    'busTime': bustime.strftime('%H:%M:%S')
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
        return DiagramData(mdate=mdateobj,arrive_time=arrive_timeobj,
                           current_num=current_num, station_id=station_id)













