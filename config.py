import os
import datetime
from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    #sqlalchemy configuration
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATION = False

    #mail configuration
    MAIL_SERVER = 'mbus.honeywell.com.cn'
    MAIL_PORT = 25
    MBUS_MAIL_SUBJECT_PREFIX = '[DoNotreply]'
    MBUS_MAIL_SENDER = 'HoneywellMobileBus'


    MBUS_ADMIN = os.environ.get('MBUS_ADMIN')
    MBUS_POSTS_PER_PAGE = 20

    #celery process use
    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'
    CELERYBEAT_SCHEDULE = {  
        'every-15-minutes': {
            'task': 'celery_worker.cleangps',
            #'schedule': datetime.timedelta(seconds=3),
            'schedule': crontab('*/15'),
            'args':("Message",)
        },
        'daily-at-midnight': {
            'task': 'celery_worker.calcbusdata',
            'schedule': datetime.timedelta(hours=3),
            #'schedule': crontab(minute=0, hour=0),
            'args':("Message",)
        },
        'daily-hours': {
            'task': 'celery_worker.unconfirmemployee',
            'schedule': datetime.timedelta(days=1),
            'args':("Message",)
        }
    }

    #for upload and download use
    UPLOAD_FOLDER = 'app/static/'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    ALLOWED_EXTENSIONS_EXCEL = set(['xls', 'xlsx', 'csv'])
    #gps allow time
    MBUS_GPS_TOCOMPANYSTART = "06:30:00"
    MBUS_GPS_TOCOMPANYEND   = "10:00:00"
    MBUS_GPS_TOHOMESTART    = "14:00:00"
    MBUS_GPS_TOHOMEEND      = "20:30:00"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:honeywell+123@localhost/shuttlebus'
        #'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_BINDS = {
        'tests':    'sqlite:///c:\hzj/04_work/14_shuttle_bus/01_research/01_web_server_flask/02_test2\shuttlebusTest/flasky/data-dev.sqlite',
        'buscard':  'mysql+pymysql://user1:HON123well@120.136.169.155/bussystem'
    }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
