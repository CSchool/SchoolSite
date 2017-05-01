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
    req.user.telegram_id = int(chat_id)
    req.user.save()
    TelegramBot.sendMessage(int(chat_id), "Добро пожаловать, {}!".format(req.user.get_full_name()))
    return redirect(reverse('index'))