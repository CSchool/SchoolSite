from celery import Celery
from main.helpers import notify_telegram, notify_email

capp = Celery('tasks', broker='amqp://cschool:cschool@localhost:5672//', backend='rpc://')


@capp.task(rate_limit='1/s')
def notify_async(telegram_id, email, subject, msg):
    notify_telegram(telegram_id, msg)
    notify_email(email, subject, msg)
