import datetime
import mimetypes
import os.path

from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseServerError

from CSchoolSite.settings import FILESERVE_MEDIA_URL, FILESERVE_METHOD, HOST


def file_response(file):
    mime = mimetypes.MimeTypes()
    mime_type = mime.guess_type(file.path)[0]
    if FILESERVE_METHOD == "django":
        f = file.file
        f.open()
        content = f.read()
        f.close()
        response = HttpResponse(content, content_type=mime_type)
    elif FILESERVE_METHOD == "xsendfile":
        response = HttpResponse(content_type=mime_type)
        response['X-Sendfile'] = file.path.encode('utf-8')
        response['Content-Length'] = file.size
    elif FILESERVE_METHOD == "nginx":
        response = HttpResponse(content_type=mime_type)
        response['X-Accel-Redirect'] = os.path.join(FILESERVE_MEDIA_URL, file.name).encode('utf-8')
        response['Content-Length'] = file.size
    else:
        raise HttpResponseServerError
    return response


def notify_telegram(id, msg):
    from telegram.bot import TelegramBot
    if id is not None:
        TelegramBot.sendMessage(id, msg, parse_mode="Markdown")


def notify_email(email, subject, msg):
    if not email:
        return
    try:
        from mistune import markdown
        html = markdown(msg)
        # add footer
        date = datetime.datetime.now().strftime('%c')
        html += '''
<hr /><br />
Это уведомление было отправлено автоматически <br />
Системное время: {date} <br />
Пожалуйста, не отвечайте на это письмо <br />
'''.format(date=date)
        send_mail(subject, msg, None, recipient_list=[email], html_message=html)
    except:
        pass


def notify_insite(user, subject, msg):
    try:
        from mistune import markdown
        html = markdown(msg)
    except:
        return None
    from main.models import Notification
    notification = Notification()
    notification.user = user
    notification.title = subject
    notification.body = html
    notification.text = msg
    notification.queued = True
    notification.save()
    return notification


def notify(user, subject, msg, async=True):
    notify_insite(user, subject, msg)
    if async:
        from CSchoolSite.celery import notify_async
        return notify_async.delay(user.telegram_id if user.notify_telegram else None,
                                  user.email if user.notify_email else None, subject, msg)
    if user.notify_email:
        notify_email(user.email, subject, msg)
    if user.notify_telegram:
        notify_telegram(user.telegram_id, msg)


def read_template(name):
    from CSchoolSite.settings import BASE_DIR
    with open(os.path.join(BASE_DIR, name)) as f:
        return f.read()


def get_sapp(req):
    if not req.user.is_authenticated:
        return None
    from applications.models import EventApplication
    apps = EventApplication.objects.filter(user=req.user, status=EventApplication.TESTING)
    for app in apps:
        if app.testing_required and app.is_general_filled:
            return app
    return None
