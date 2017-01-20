from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from CSchoolSite import settings
from main.enums import REQUEST_STATUS
from main.enums import WAITING
from main.validators import PhoneValidator

# Create your models here.


class User(AbstractUser):
    patronymic = models.CharField(_('patronymic'), max_length=30, null=True, blank=True, default='')
    birthday = models.DateField(_('birthday'), null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=18, null=True, blank=True, default='',
                             validators=[PhoneValidator()])

    def get_initials(self):
        full_name = '%s %s %s' % (self.last_name, self.first_name, self.patronymic)
        return full_name.strip()


class Relationship(models.Model):
    class Meta:
        verbose_name = _('Family relative')
        verbose_name_plural = _('Family relatives')

    relative = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="related_user", verbose_name=_('Relative'))
    child = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="child_user", verbose_name=_('Child'))
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invited_user", verbose_name=_('Invited user'))

    code = models.CharField(max_length=10, verbose_name=_('Invite code'))
    status = models.CharField(max_length=2, choices=REQUEST_STATUS, default=WAITING, verbose_name=_('Status'))

    def __str__(self):
        return self.id