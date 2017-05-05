from celery import Celery
import os
from main.helpers import notify_telegram, notify_email

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CSchoolSite.settings')

app = Celery('CSchoolSite')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()


@app.task(rate_limit='1/s')
def notify_async(telegram_id, email, subject, msg):
    notify_telegram(telegram_id, msg)
    notify_email(email, subject, msg)
