from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from userprofile.models import User

from telegram.bot import TelegramBot, digest

@login_required
def auth_view(req, chat_id, checksum):
    if checksum != digest(chat_id):
        raise PermissionDenied
    if req.user.telegram_id is not None:
        raise PermissionDenied
    if User.objects.filter(telegram_id=chat_id).exists():
        raise PermissionDenied
    req.user.telegram_id = int(chat_id)
    req.user.telegram_username = TelegramBot.getChat(int(chat_id)).get('username')
    req.user.save()
    TelegramBot.sendMessage(int(chat_id), "Добро пожаловать, {}!".format(req.user.get_full_name()))
    return redirect(reverse('user_profile'))


@login_required
def unlink_view(req):
    req.user.telegram_id = None
    req.user.telegram_username = None
    req.user.save()
    return redirect(reverse('user_profile'))