from flask_mail import Message
from flask_mail import Mail


def send_email(to, subject):
    msg = Message(app.config['MBUS_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['MBUS_MAIL_SENDER'],
                  recipients=[to])
    msg.body = 'text body'
    msg.html = '<b>HTML</b> body'
    mail.send(msg)