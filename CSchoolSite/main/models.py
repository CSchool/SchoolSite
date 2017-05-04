from django.db import models
from django.utils import timezone

from userprofile.models import User


class Notification(models.Model):
    title = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField()

    queued = models.BooleanField(blank=True, default=False, db_index=True)

    TYPE = 'NOTIFICATION'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Notification, self).save(*args, **kwargs)
