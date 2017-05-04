import mimetypes
import os.path
import datetime

from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseServerError

from CSchoolSite.settings import FILESERVE_MEDIA_URL, FILESERVE_METHOD

HOST = 'https://olimp-nw.ru'
try:
    from telegram.bot import HOST
except ImportError:
    try:
        from CSchoolSite.settings import HOST
    except ImportError:
        try:
            from CSchoolSite.personalsettings import HOST
        except ImportError:
            pass


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


def notify_telegram(user, msg):
    from telegram.bot import TelegramBot
    id = user.telegram_id
    if id is not None:
        TelegramBot.sendMessage(id, msg, parse_mode="Markdown")


def notify_email(user, subject, msg):
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
        if user.email:
            send_mail(subject, msg, None, recipient_list=[user.email], html_message=html)
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


def notify(user, subject, msg, queue=True):
    if queue:
        notify_insite(user, subject, msg)
    else:
        notify_email(user, subject, msg)
        notify_telegram(user, msg)


def read_template(name):
    from CSchoolSite.settings import BASE_DIR
    with open(os.path.join(BASE_DIR, name)) as f:
        return f.read()