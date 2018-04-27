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


@celery.task
def send_async_email(params):
    msg = Message(current_app.config['MBUS_MAIL_SUBJECT_PREFIX'] + ' ' + params['subject'],
                sender=current_app.config['MBUS_MAIL_SENDER'], recipients=[params['to']])
    msg.body = params['msg_body']
    msg.html = params['msg_html']
    mail.send(msg)


def send_email(to, subject, template, **kwargs):
    #return mail.send(msg)
    #celery delay args default serializer is JSON
    params = {
        "to": to,   
        "subject": subject,
        "msg_body": render_template(template + '.txt', **kwargs),
        "msg_html": render_template(template + '.html', **kwargs)
    }
    send_async_email.delay(params)
'''

def send_email(to, subject, template, **kwargs):
    #return mail.send(msg)
    #celery delay args default serializer is JSON
    msg = Message(current_app.config['MBUS_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                sender=current_app.config['MBUS_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    return mail.send(msg)


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
