import os
from threading import Thread
from flask_mail import Message
from arrotechtools import ErrorHandler
from app.extensions import mail
from app.__init__ import create_app
import os
from app.celery import make_celery


app = create_app(os.environ.get('FLASK_ENV', default='development'))
celery = make_celery(app)


def send_async_email(app, msg):
    """Send asychronous email."""
    with app.app_context():
        try:
            mail.send(msg)
        except ConnectionRefusedError:
            return ErrorHandler.raise_error('Mail server not working', 500)


@celery.task(name='mail.send_email')
def send_email(subject, sender, recipients, text_body, html_body):
    """Message body."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
