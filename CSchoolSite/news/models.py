from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class NewsPost(models.Model):
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        permissions = (
            ("view_period", "Возможность просматривать новости"),
        )

    title = models.CharField(max_length=250, verbose_name="Название")
    body = models.TextField(verbose_name="Текст")
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, verbose_name="Добавивший пользователь")
    created = models.DateTimeField(editable=False, verbose_name="Дата создания")
    modified = models.DateTimeField(verbose_name="Дата изменения")

    def __str__(self):
        return "%r" % self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(NewsPost, self).save(*args, **kwargs)
