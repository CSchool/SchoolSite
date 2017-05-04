from django.core.management.base import BaseCommand
from queue import Queue

from main.models import Notification
from main.helpers import notify


class Command(BaseCommand):
    help = 'Runs notification queue'

    def handle(self, *args, **options):
        import time

        queue = Queue()

        while 1:
            if queue.empty():
                # Refill from DB
                q = Notification.objects.filter(queued=True)
                for notification in q:
                    queue.put(notification)
            else:
                notification = queue.get()
                notification.queued = False
                notification.save()
                notify(notification.user, notification.title, notification.body, queue=False)

            time.sleep(1) # Sleep for evading limits (mail, telegram etc)

