from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import jsonify, current_app, g
from ..models import mBus
from .errors import unauthorized
from . import api

auth = HTTPTokenAuth(scheme='Bearer')

def generate_auth_token_gps(expiration):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({'gpsuser': 'gpsuser'}).decode('utf-8')

def verify_auth_token_gps(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return None
    return data.get(data['gpsuser'])

@auth.verify_token
def verify_token(token):
    g.current_user = None
    try:
        data = verify_auth_token_gps(token)
    except:
        return False

    if data is not None:
        if 'gpsuser' in data:
            g.current_user = True
            return True
    return False

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.route('/token')
def get_token():
    tokengen = generate_auth_token_gps(expiration=600)
    return jsonify({'token': tokengen})
