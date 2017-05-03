from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from CSchoolSite import settings


class NewsPost(models.Model):
    class Meta:
        verbose_name = _('News post')
        verbose_name_plural = _('News posts')
        permissions = (
            ("view_news", _("view news")),
        )
    title = models.CharField(max_length=250, verbose_name=_('Title'))
    body = models.TextField(verbose_name=_('Body'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE, verbose_name=_('Submitted user'))
    created = models.DateTimeField(editable=False, verbose_name=_('Posted at'))
    modified = models.DateTimeField(verbose_name=_('Modified at'))

    TYPE = 'NEWSPOST'

    def __str__(self):
        return "%r" % self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(NewsPost, self).save(*args, **kwargs)
