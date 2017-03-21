#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app, render_template
from flask_mail import Message
from . import mail, flask_celery


def send_async_email(app, msg):

    '''
        send the email in async mode
    :param msg: the email
    :return: None
    '''

    pass

@flask_celery.task(
    bind=True,
    igonre_result=True,
    default_retry_delay=300,
    max_retries=5
)
def send_email(self, to, subject, template, username, token):

    '''
        deal with the operation of sending emails
    :param to: eamil address od the recipient
    :param subject: the subject
    :param template: template name
    :param kwargs: kwargs
    :return: None
    '''

    #print kwargs
    #print two
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template+'.txt', username=username, token=token)
    msg.html = render_template(template+'.html', username=username, token=token)
    with app.app_context():
        mail.send(msg)
