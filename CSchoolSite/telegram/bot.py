import telepot
import hashlib

from django.urls import reverse
from django.core import signing
from CSchoolSite.settings import SECRET_KEY, HOST
from CSchoolSite.settings import TELEGRAM_TOKEN as TOKEN

from userprofile.models import User

TelegramBot = telepot.Bot(TOKEN)


def digest(id):
    m = hashlib.sha256()
    m.update(SECRET_KEY.encode())
    m.update(str(id).encode())
    return m.hexdigest()[:16]


def decode_deeplink(arg):
    try:
        sp = arg.split('_')
        assert len(sp) == 2
        assert digest(sp[0]) == sp[1]
        return User.objects.get(id=sp[0])
    except:
        return None


def get_link(chat_id):
    return "https://olimp-nw.ru{}".format(reverse('telegram_auth', args=[chat_id, digest(chat_id)]))


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if chat_type != 'private':
        TelegramBot.sendMessage(chat_id, '''
Этот бот пока работает только в личных чатах
''')
        return

    if content_type == 'text':
        t = msg['text']
        sp = t.split()
        if len(sp) > 0 and sp[0] == '/start':
            if len(sp) > 1:
                arg = sp[1]
            else:
                arg = None
            user = decode_deeplink(arg)
            if user:
                user.telegram_id = chat_id
                chat = TelegramBot.getChat(chat_id)
                user.telegram_username = chat.get('username')
                user.save()
                TelegramBot.sendMessage(chat_id, '''
Привет, {name}!
'''.format(name=user.get_full_name()))
                return

        try:
            user = User.objects.get(telegram_id=chat_id)
        except User.DoesNotExist:
            TelegramBot.sendMessage(chat_id, '''
Для использования бота сайта {host}, вам необходимо привязать ваш Telegram аккаунт.

Для этого пройдите по [ссылке]({link})
        '''.format(link=get_link(chat_id), host=HOST), parse_mode='Markdown')
            return

        if t == '/help':
            TelegramBot.sendMessage(chat_id, '''
*Список команд*
/help - вывести эту справку
/unlink - отвязать аккаунт _{username}_
'''.format(username=user.username), parse_mode='Markdown')

        elif t == '/unlink':
            user.telegram_id = None
            user.telegram_username = None
            user.save()
            TelegramBot.sendMessage(chat_id, '''
Пока, {first_name}. Если я понадоблюсь снова, просто напиши мне что-нибудь :)
'''.format(first_name=user.first_name))

        else:
            TelegramBot.sendMessage(chat_id, '''
Я тебя не понял. Может быть попробуешь /help для списка команд?
''')
    else:
        TelegramBot.sendMessage(chat_id, '''
Я тебя не понял. Пиши пожалуйста текстом :)
''')
