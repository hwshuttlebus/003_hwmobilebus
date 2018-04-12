import os
from app import create_app, db
from app.models import mUser, mRole, mPost, Permission
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from celery import Celery

#support websocket
from flask_socketio import SocketIO, emit
from flask import session



app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

#support websocket
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    print('!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(message['data'].encode('utf-8'))
    print('mode:')
    print(socketio.async_mode)
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)

def make_shell_context():
    return dict(app=app, db=db, mUser=mUser, mRole=mRole, mPost=mPost,
                Permission=Permission)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

#flask scripts runserver  task cannot be used with flask-socketio, which has
#its own way to start the server.
#so here use another way to decorate socketio into manager
#start command:
#python manage.py run
@manager.command
def run():
    socketio.run(app=app,
                host='127.0.0.1',
                port=5000,
                use_reloader=False)

if __name__ == '__main__':
    #support websocket
    #socketio.run(app, debug=True)
    manager.run()