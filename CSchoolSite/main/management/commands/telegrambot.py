from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs telegram bot'

    def handle(self, *args, **options):
        import time
        from telegram.bot import TelegramBot, handle

        TelegramBot.message_loop(handle)
        while 1:
            time.sleep(10)