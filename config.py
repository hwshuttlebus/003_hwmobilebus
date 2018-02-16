import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATION = False

    MAIL_SERVER = 'mail.hwmobilebus.tk'
    MAIL_PORT = 25

    MBUS_MAIL_SUBJECT_PREFIX = '[DoNotreply]'
    MBUS_MAIL_SENDER = 'HoneywellMobileBus'
    MBUS_ADMIN = os.environ.get('MBUS_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:honeywell+123@localhost/shuttlebus'
        #'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_BINDS = {
        'tests':    'sqlite:///c:\hzj/04_work/14_shuttle_bus/01_research/01_web_server_flask/02_test2\shuttlebusTest/flasky/data-dev.sqlite'
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
