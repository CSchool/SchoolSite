import telepot
import hashlib

from django.urls import reverse

from userprofile.models import User

TOKEN_PATH = '/etc/cschoolsite_telegram_token'
TOKEN = 'NOT APPLICABLE'
HOST = 'https://olimp-nw.ru'

try:
    with open(TOKEN_PATH, 'r') as f:
        TOKEN = f.read().strip()
except:
    pass

TelegramBot = telepot.Bot(TOKEN)


def digest(id):
    m = hashlib.sha256()
    m.update(TOKEN.encode())
    m.update(str(id).encode())
    return m.hexdigest()[:16]


def get_link(chat_id):
    return "https://olimp-nw.ru{}".format(reverse('telegram_auth', args=[chat_id, digest(chat_id)]))


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    # first, determine who is sending this message
    try:
        user = User.objects.get(telegram_id=chat_id)
    except User.DoesNotExist:
        TelegramBot.sendMessage(chat_id, '''
Для использования бота сайта olimp-nw.ru, вам необходимо привязать ваш Telegram аккаунт.

Для этого пройдите по [ссылке]({})
'''.format(get_link(chat_id)), parse_mode='Markdown')
        return

    if chat_type != 'private':
        TelegramBot.sendMessage(chat_id, '''
Этот бот пока работает только в личных чатах
''')
        return

    if content_type == 'text':
        t = msg['text']
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
