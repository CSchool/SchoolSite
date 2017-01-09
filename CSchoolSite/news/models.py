from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class NewsPost(models.Model):
    class Meta:
        verbose_name = _('News post')
        verbose_name_plural = _('News posts')
    title = models.CharField(max_length=250, verbose_name=_('Title'))
    body = models.TextField(verbose_name=_('Body'))
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, verbose_name=_('Submitted user'))
    created = models.DateTimeField(editable=False, verbose_name=_('Posted at'))
    modified = models.DateTimeField(verbose_name=_('Modified at'))

    def __str__(self):
        return "%r" % self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(NewsPost, self).save(*args, **kwargs)
