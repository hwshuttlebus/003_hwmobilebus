from flask_mail import Message
from flask_mail import Mail
from flask import render_template, current_app
from threading import Thread
import requests, json
from . import mail

'''
def send_email(to, subject):
    msg = Message(app.config['MBUS_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['MBUS_MAIL_SENDER'],
                  recipients=[to])
    msg.body = 'text body'
    msg.html = '<b>HTML</b> body'
    mail.send(msg)
'''


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MBUS_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MBUS_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_async_email_cloud(app, params, url):
    with app.app_context():
        r = requests.post(url, files={}, data=params)
        #print(r.text)

def send_email_cloud(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    url = "http://api.sendcloud.net/apiv2/mail/send"
    msg_html = render_template(template + '.html', **kwargs)
    params = {"apiUser": "shuttlebustest_test_mgKiln", \
              "apiKey": "urz9OUM79PfVY4b5", \
              "from": "service@sendcloud.im", \
              "fromName": "ShuttleBus System", \
              "to": to, \
              "subject": subject, \
              "html": msg_html, \
              }
    thr = Thread(target=send_async_email_cloud, args=[app, params, url])
    thr.start()
    return thr
