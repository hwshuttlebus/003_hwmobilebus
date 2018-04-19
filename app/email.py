from flask_mail import Message
from flask_mail import Mail
from flask import render_template, current_app
from threading import Thread
import requests, json
from . import mail, celery


'''
def send_email(to, subject):
    msg = Message(app.config['MBUS_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['MBUS_MAIL_SENDER'],
                  recipients=[to])
    msg.body = 'text body'
    msg.html = '<b>HTML</b> body'
    mail.send(msg)
'''

@celery.task
def send_async_email(msg):
    mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MBUS_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MBUS_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    #return mail.send(msg)
    send_async_email.delay(msg)


@celery.task
def send_async_email_cloud(params, url):
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
    send_async_email_cloud.delay(params, url)
