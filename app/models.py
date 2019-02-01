from . import db
from . import login_manager
from datetime import datetime, timedelta, date
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

# pre_gps_timestamp = [0] * 301
# timeout_check = 0
gPreCurDist = {}

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
    def updatediagram(station):
        currbeijingtime = get_currbj_time()
        #update date
        mdateobj = currbeijingtime.date()
        #update time
        mtimeobj = currbeijingtime.time()

        diagramrec = DiagramData.query.filter_by(mdate=mdateobj, station_id=station.id).all()

        def deltaFromArrivalTime(dia):
            # station = mStation.query.filter_by(id=dia.station_id).first()
            t1 = station.time
            t2 = dia.arrive_time
            return abs(datetime.combine(date.today(),t1)-datetime.combine(date.today(),t2))

        nearestTime = min(diagramrec, key=deltaFromArrivalTime)

        # if new arrival time is nearer to expected arrival time than existing record.
        new_diagramrec = DiagramData(mdate=mdateobj, arrive_time=mtimeobj,current_num=0, station_id=station.id)
        if nearestTime > deltaFromArrivalTime(new_diagramrec):
            #current number will update in celery task
            # print(new_diagramrec.to_json())
            db.session.add(new_diagramrec)
            db.session.commit()

    @staticmethod
    def fakediagram():
        currbeijingtime = get_currbj_time()
        #update date
        mdateobj = currbeijingtime.date()
        #in bus time
        timestr1 = [('07:28:10', 729, '2018-04-10', 5),('07:38:10', 729, '2018-04-11', 4),
                    ('07:33:10', 729, '2018-04-13', 0),('07:32:10', 729, '2018-04-14', 2),
                    ('07:45:01',730, '2018-04-10', 10 ),
                    ('07:46:01',731, '2018-04-10', 11 ),
                    ('08:45:01',735, '2018-04-10', 20 ),('08:25:01',735, '2018-04-11', 22 ),
                    ('08:20:01',735, '2018-04-12', 30 ),('08:25:01',735, '2018-04-13', 22 ),

                    ('08:28:10', 78, '2018-04-20', 25),('08:38:20', 78, '2018-04-21', 34),
                    ('08:33:10', 78, '2018-04-23', 20),('08:32:20', 78, '2018-04-24', 12),
                    ('07:45:01',80, '2018-04-20', 5 ),
                    ('07:46:01',81, '2018-04-20', 0 ),
                    ('08:01:01',82, '2018-04-20', 12 ),('08:05:01',82, '2018-04-21', 12 ),
                    ('08:20:01',83, '2018-04-22', 3 ),('08:07:01',83, '2018-04-23', 2 )]

        timestr2 = [('17:12:10', 736, '2018-04-10', 22),('17:11:10', 736, '2018-04-11', 20),
                    ('17:10:10', 736, '2018-04-12', 21),('17:12:10', 736, '2018-04-13', 18),
                    ('17:51:01',737, '2018-04-10', 0),('17:52:01',737, '2018-04-11', 0),
                    ('17:52:01',738, '2018-04-10', 0),('17:53:01',739, '2018-04-13', 0),
                    ('17:55:01',740, '2018-04-10', 0),('17:59:01',740, '2018-04-14', 0),

                    ('17:12:10', 79, '2018-04-20', 32),('17:11:10', 79, '2018-04-21', 20),
                    ('17:10:10', 79, '2018-04-22', 41),('17:12:10', 79, '2018-04-23', 18),
                    ('17:51:01',85, '2018-04-20', 0),('17:52:01',85, '2018-04-21', 0),
                    ('17:52:01',86, '2018-04-20', 0),('17:53:01',86, '2018-04-23', 0),
                    ('17:55:01',87, '2018-04-20', 0),('17:59:01',87, '2018-04-24', 0)]


        timestr1obj = []
        timestr2obj = []
        for item in timestr1:
            timestr1obj.append((datetime.strptime(item[0], '%H:%M:%S').time(), item[1],
                                datetime.strptime(item[2], '%Y-%m-%d').date(),item[3]))
        for item2 in timestr2:
            timestr2obj.append((datetime.strptime(item2[0], '%H:%M:%S').time(), item2[1],
                                datetime.strptime(item2[2], '%Y-%m-%d').date(), item2[3]))
        #duplicate
        '''
        timestr3 = [('07:40:01', 48),('07:45:03',50)]
        timestr4 = [('18:08:12',57)]
        timestr3obj = []
        timestr4obj = []
        for item in timestr3:
            timestr1obj.append((datetime.strptime(item[0], '%H:%M:%S').time(), item[1]))
        for item2 in timestr4:
            timestr2obj.append((datetime.strptime(item2[0], '%H:%M:%S').time(), item2[1]))
        '''

        for item3 in timestr1obj:
            print(item3)
            diagramrec = DiagramData(mdate=item3[2],
                                     arrive_time=item3[0],
                                     current_num=item3[3],
                                     station_id=item3[1])
            db.session.add(diagramrec)
            db.session.commit()

        for item4 in timestr2obj:
            print(item4)
            diagramrec = DiagramData(mdate=item4[2],
                                     arrive_time=item4[0],
                                     current_num=item4[3],
                                     station_id=item4[1])
            db.session.add(diagramrec)
            db.session.commit()

    @staticmethod
    def locCoreAlgorithm(current_station_index, lefttime, busrec, station, lon, lat):

        global gPreCurDist
        next_station_index = current_station_index + 1
        number_of_stations = len(station)
        final_station_index = number_of_stations - 1
        averagespeed = 15#about 60km/h bus average speed
        nowtimetk = time.time()

        # print('!!!current location: '+str(lon)+', '+str(lat))
        # print('!!!station[next_station_index].lon, station[next_station_index].lat:'+str(station[next_station_index].lon)+', '+str(station[next_station_index].lat))

        if busrec.abntime is None:
            abntime = 0.0
        else:
            abntime = busrec.abntime

        # At the beginning, abnleftdist is designed to record distance from bus
        # to next station when abnormal condition occur. This value now is used
        # to record the distance from bus to current station in each frame to
        # help determine if the bus is getting closer to the current station
        # which is another abnormal condition.
        if busrec.abnleftDist is None:
            abnleftDist = 0.0
        else:
            abnleftDist = busrec.abnleftDist
        if busrec.lefttime is None:
            busreclefttime = 0.0
        else:
            busreclefttime = busrec.lefttime

        dist_to_cur_station = 10000.0

        if next_station_index <= final_station_index and current_station_index >= -1:
            # -1 meanst the bus haven't arrive the first station
            abnormal = False

            dist_to_next_station = haversine(lon, lat, station[next_station_index].lon, station[next_station_index].lat)
            lefttime = (dist_to_next_station*1.5/averagespeed)/60 # unit-->minute
            print('!!!starting calcuate: bus_number={}, dist_to_next_station={}, lefttime={}, busreclefttime={}'.format(busrec.number,dist_to_next_station, lefttime, busreclefttime))

            # If remaining time to next station is greater than the remaining time in last frame of GPS,
            # it means the bus is further away from the next station. It's a abnormal condition. 0.1 and 1/60
            # is used to exclude debounce of GPS.
            if (busreclefttime > 0.1) and (busreclefttime + 1/60  < lefttime):
                print('!!!ABNORMAL: To next station, busnumber={}, distance={}, time={}, previous time={}'.format(busrec.number, dist_to_next_station, lefttime, busreclefttime))
                abnormal = True

            if current_station_index != -1:
                if busrec.id not in gPreCurDist.keys():
                    gPreCurDist[busrec.id] = 10000
                pre_dist_to_cur_station = gPreCurDist[busrec.id]

                dist_to_cur_station = haversine(lon, lat, station[current_station_index].lon, station[current_station_index].lat)
                print('!!!starting calcuate 2: bus_number={}, dist_to_cur_station={}, pre_dist_to_cur_station={}'.format(busrec.number,dist_to_cur_station,pre_dist_to_cur_station))
                # If the distance to current station is less than the distance in last frame of GPS, it means
                # the bus is getting closer to the station that it should apart from. It's another abnormal condition.
                # We consider this condition only after we have got the first station and when the bus left the
                # current station more than 100 meters. And minus 1 seconds distance is used to exclude debounce of GPS.
                if pre_dist_to_cur_station > 100 and dist_to_cur_station < pre_dist_to_cur_station - averagespeed:
                    print('!!!ABNORMAL: To current station, busnumber={}, distance={}, previous distance={}'.format(busrec.number, dist_to_cur_station, pre_dist_to_cur_station))
                    abnormal = True

            if abnormal:
                # In abnormal case, handle based on abnormal duration.
                if abntime == 0.0:
                    #the first time abnormal only record time tick and leftDistance
                    abntime = nowtimetk
                    print('!!!first time enter abnormal, bus_number={}, timestamp={}'.format(busrec.number, abntime))
                else:
                    print('!!!abnormal status, bus_number={}, duration={}'.format(busrec.number, int(nowtimetk - abntime)))
                    if ((nowtimetk - abntime) >= 30):
                        # Abnormal duration last more than 30 seconds, the bus is always far from dest station
                        # recalculate the current station once
                        abntime = nowtimetk
                        old_index = current_station_index
                        current_station_index = mBus.getcurstation(current_station_index, station, lon, lat)
                        next_station_index = current_station_index + 1
                        if current_station_index != -1:
                            dist_to_cur_station = haversine(lon, lat, station[current_station_index].lon, station[current_station_index].lat)
                            mBus.updatediagram(station[current_station_index])
                        if current_station_index < final_station_index:
                            dist_to_next_station = haversine(lon, lat, station[next_station_index].lon, station[next_station_index].lat)
                            lefttime = (dist_to_next_station*1.5/averagespeed)/60
                        else:
                            lefttime = 0
                        print('!!!ABNORMAL recalculate: bus_number={}, oldcurindex={}, newcurindex={},dist_to_next_station={},lefttime={}'.format(busrec.number, old_index, current_station_index, dist_to_next_station, lefttime))
            else:
                #normal case
                #if in abnormal case before, regard enter normal state when following condition meet:
                #   during 10 seconds the bus location is near to dest station
                # if ((nowtimetk-abntime)<=10) and (abntime!=0):
                print('!!!normal state, bus_number={}, now={}, abntime={}, dir={}, curindex={}, disttonext={}'.format(busrec.number, nowtimetk, abntime, busrec.currdir, current_station_index, dist_to_next_station))
                abntime = 0.0
                if dist_to_next_station <= 100.0 \
                        or (busrec.currdir == False and current_station_index == -1 and dist_to_next_station <= 300.0)\
                        or (busrec.currdir == True and next_station_index == final_station_index and dist_to_next_station <= 300.0):
                    #arrived and index to next station
                    current_station_index = next_station_index
                    dist_to_cur_station = haversine(lon, lat, station[current_station_index].lon, station[current_station_index].lat)
                    print('!!!#arrived to next station: bus_number={},station index={}'.format(busrec.number,current_station_index))
                    mBus.updatediagram(station[current_station_index])
                    if current_station_index < final_station_index:
                        dist_to_next_station = haversine(lon, lat, station[next_station_index].lon, station[next_station_index].lat)
                        lefttime = (dist_to_next_station*1.5/averagespeed)/60 # unit-->minute
                    else:
                        lefttime = 0
        gPreCurDist[busrec.id] = dist_to_cur_station
        # abnleftDist = dist_to_cur_station
        return current_station_index, lefttime, abntime, abnleftDist

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
    def getcurstation(curindex, stations, lon, lat):
        '''
        The nearest station might be the current station or the next station,
        Say two adjacent stations S1 and S2, the distance from bus to S1 is d1,
        and from bus to S2 is d2, from S1 to S2 is d12. When (d1+d2)/d12 is the
        smaller in all adjacent stations, S1 should be the current station.
        '''
        nearest_station_index = mBus.getnearstation(stations, lon, lat)
        print("!!!Get current station: nearest station index:{}".format(nearest_station_index))
        if nearest_station_index == 0:
            return 0
        if nearest_station_index == len(stations) - 1:
            return nearest_station_index - 1

        S1 = stations[nearest_station_index - 1]
        S2 = stations[nearest_station_index]
        S3 = stations[nearest_station_index + 1]

        d1 = haversine(S1.lon, S1.lat, lon, lat)
        d2 = haversine(S2.lon, S2.lat, lon, lat)
        d3 = haversine(S3.lon, S3.lat, lon, lat)

        d12 = haversine(S1.lon, S1.lat, S2.lon, S2.lat)
        d23 = haversine(S2.lon, S2.lat, S3.lon, S3.lat)

        R1 =  (d1+d2)/d12
        R2 =  (d2+d3)/d23
        print("!!!d1={},d2={},d3={},d12={},d23={},R1={},R2={}".format(d1,d2,d3,d12,d23,R1,R2))

        if R1<R2:
            return nearest_station_index-1
        else:
            return nearest_station_index

        # retindex = 0
        # dists_bus2station= []
        # dists_station2station= []
        # ratio = 100
        # if curindex < 0:
            # # if the target station is the first station and the bus is further away
            # # set the first station as the current station.
            # return 0
        # #iterate stations
        # for idx in range(curindex, len(stations)):
        # # for idx, item in enumerate(stations):
            # s1 = stations[idx]
            # if s1.name is not None and s1.lat is not None and s1.lon is not None:
                # dists_bus2station.append(haversine(s1.lon, s1.lat, lon, lat))
                # if idx < len(stations) - 1:
                    # s2 = stations[idx+1]
                    # if s2.name is not None and s2.lat is not None and s2.lon is not None:
                        # dists_station2station.append(haversine(s1.lon, s1.lat, s2.lon, s2.lat))
        # for i in range(len(dists_station2station)):
            # x = (dists_bus2station[i]+dists_bus2station[i+1])/dists_station2station[i]
            # # print('!!ZZZ!!recal: index={}, d1+{}, d2={}, d3={}, ratio={}'.format(curindex+i,dists_bus2station[i],dists_bus2station[i+1],dists_station2station[i],x))
            # if x < ratio:
                # ratio = x
                # retindex = curindex+i
        # return retindex

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

    # @staticmethod
    # def check_timeout(now_ts):
        # global pre_gps_timestamp, timeout_check
        # if timeout_check == 0:
            # timeout_check = now_ts
            # return
        # if now_ts - timeout_check <= 60:
            # return

        # updatedb = False
        # buses = mBus.query.all()
        # for busrec in buses:
            # if busrec.curridx != 0xFF and now_ts - pre_gps_timestamp[busrec.number] > 60:
                # #timeout
                # busrec.curridx = 0xFF
                # pre_gps_timestamp[busrec.number] = 0
                # db.session.add(busrec)
                # updatedb = True
                # print("!!!TIMEOUT: bus number:{}, previous GPS signal timestamp:{}".format(busrec.number, pre_gps_timestamp[busrec.number]))
        # if updatedb:
            # db.session.commit()
        # timeout_check = now_ts

    def is_working_time(self):
        if self.number == 300:
            #for testing
            return True
        stationup = []
        stationdown = []
        stations = self.stations.order_by(mStation.time).all()
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
        nowtime = nowtime.replace(tzinfo=None)
        if (((nowtime >= towkstartoffsetobj) and (nowtime <= towkendoffsetobj)) or
             ((nowtime >= tohmstartoffsetobj) and (nowtime <= tohmendoffsetobj))):
            return True
        else:
            return False

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

        print('!!!current time:{}'.format(nowtime))
        nowtime = nowtime.replace(tzinfo=None)

        # global pre_gps_timestamp
        # now_ts = datetime.timestamp(nowtime)
        # pre_gps_timestamp[busrec.number] = now_ts

        TESTING = False
        if busrec.number == 300:
            # for testing
            TESTING = True

        #ENTER CORE ASSESSMENT ALGUORITHM
        if (((nowtime >= towkstartoffsetobj) and (nowtime <= towkendoffsetobj)) or
             ((nowtime >= tohmstartoffsetobj) and (nowtime <= tohmendoffsetobj))) or TESTING:
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
                if ((datetimeobj >= tohmstartoffsetobj) and (datetimeobj <= tohmendoffsetobj)) or TESTING:
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
                    currentidx, lefttime, abntime, abnleftDist = mBus.locCoreAlgorithm(currentidx, lefttime, busrec, station, lon, lat)
                    print('!!!GPS data recv before arrive at first stop: bus_number={}, curindex={}, lefttime={}, abntime={}, distocur={}'.format(busrec.number, currentidx, lefttime, abntime, abnleftDist))
                else:
                    #GPS data recv after the first stop
                    #should find the nearest station index for current bus location
                    currentidx = mBus.getcurstation(currentidx, station, lon, lat)
                    mBus.updatediagram(station[currentidx])
                    print('!!!GPS data recv after the first stop latest index is:' +str(currentidx))
            else:
                #already recv valid gps data after enter shuttle bus time
                #re-calculate the left distance and left time
                currentidx = busrec.curridx
                print('!!!normal case before:bus_number={}, curindex={}, lefttime={}, abntime={}, distocur={}'.format(busrec.number, busrec.curridx, busrec.lefttime, busrec.abntime, busrec.abnleftDist))
                currentidx, lefttime, abntime, abnleftDist = mBus.locCoreAlgorithm(currentidx, lefttime, busrec, station, lon, lat)
                print('!!!normal case after:bus_number={}, curindex={}, lefttime={}, abntime={}, distocur={}, currdir={}'.format(busrec.number, currentidx, lefttime, abntime, abnleftDist, currdir))

        else:
            # mBus.check_timeout(now_ts)
            #not in shuttle bus time, return invalid data
            print('!!!not in shuttle bus time, return invalid data, currentidx={}'.format(currentidx))

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

        if recordtime is not None:
            #transfer from UTC to Asia/Shanghai native time
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('Asia/Shanghai')
            try:
                datetimeobj = datetime.strptime(recordtime.strip(), '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                #if the timestamp of gps device don't send date, the utc date will be used as current date.
                datetimeobj = datetime.strptime(recordtime.strip(), '%H:%M:%S')
                utcnowtime= datetime.utcnow()
                datetimeobj = datetimeobj.replace(year=utcnowtime.year, month=utcnowtime.month, day=utcnowtime.day)
            datetimeobj = datetimeobj.replace(tzinfo=from_zone)
            datetimeobj = datetimeobj.astimezone(to_zone)
            datetimeobj = datetimeobj.replace(tzinfo=None)
            print('!!!current gps data: '+ str(equip_id) + ', ' +str(latwsg)+', '+str(lngwsg)+', '+ str(datetimeobj))
        else:
            datetimeobj = datetime.strptime('2000-01-01T12:12:12', '%Y-%m-%dT%H:%M:%S')

        #update
        busrec = mBus.query.filter_by(equip_id=equip_id).first()
        if busrec is not None:
            station = busrec.stations.first()
            if haversine(lon, lat, station.lon, station.lat) > 100000:
                return None
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
        self.member_since = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
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
        bus1 = ""
        bus2 = ""
        station1 = ""
        station2 = ""
        stations = self.stations.all()
        if stations is not None:
            if len(stations) >= 1:
                if stations[0] is not None:
                    station1 = stations[0].name
                    busrec1 = mBus.query.filter_by(id=stations[0].bus_id).first()
                    if busrec1 is not None:
                        bus1 = busrec1.name
            if len(stations) >= 2:
                if stations[1] is not None:
                    station2 = stations[1].name
                    busrec2 = mBus.query.filter_by(id=stations[1].bus_id).first()
                    if busrec2 is not None:
                        bus2 = busrec2.name

        json_post = {
            'id' : self.id,
            'mailaddr' : self.mailaddr,
            'campus': self.campus,
            'role_id': self.role_id,
            'role_name': self.mrole.name,
            'reg_bus1': bus1,
            'reg_bus2': bus2,
            'reg_station1': station1,
            'reg_station2': station2
        }
        return json_post

    def to_json_apply(self):
        json_post = {
            'id': self.id,
            'mailaddr': self.mailaddr,
            'applyflag': self.applyflag,
            'applydesc': self.applydesc,
            'lat': self.lat,
            'lon': self.lon
        }
        return json_post

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_json(self):
        json_post = {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp.strftime('%Y-%m-%dT%H:%M:%S')+'+0000'
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Message(body=body)



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













