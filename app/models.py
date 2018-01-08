from . import db
from datetime import datetime
from .exceptions import ValidationError

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
































