from datetime import datetime

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from CSchoolSite import settings
from main.validators import PhoneValidator

from applications.models import Period
from userprofile.utils import is_group_member



class User(AbstractUser):
    patronymic = models.CharField(_('patronymic'), max_length=30, null=True, blank=True, default='')
    birthday = models.DateField(_('birthday'), null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=18, null=True, blank=True, default='',
                             validators=[PhoneValidator()], help_text=_('The format of phone numbers is +7 (123) 456-78-90'))

    personal = models.BooleanField(_('Account is personal'), null=False, blank=False, default=True,
                                   help_text=_("Enable user profile and social/personal actions"))

    alias = models.CharField(_('Alias'), max_length=250, null=True, blank=True, default='',
                             help_text=_('Use contents of this field instead of username'))

    def get_initials(self):
        full_name = '%s %s %s' % (self.last_name or '', self.first_name or '', self.patronymic or '')
        return full_name.strip()

    def get_aliased_username(self):
        return self.alias if self.alias else self.username

    def is_eligible_for_application(self, period=None):
        if not self.is_authenticated():
            return False
        if not self.personal:
            return False
        if not self.is_parent:
            return False
        if period:
            return period.registration_open
        return bool(Period.objects.filter(registration_begin__lt=datetime.now(), registration_end__gt=datetime.now()))

    def is_eligible_for_application_viewing(self):
        if not self.is_authenticated():
            return False
        if not self.personal:
            return False
        return bool(Period.objects.filter(registration_begin__lt=datetime.now(), registration_end__gt=datetime.now()))

    @property
    def is_parent(self):
        return is_group_member(self, _('Parents'))

    @property
    def is_student(self):
        return is_group_member(self, _('Students'))

    @property
    def is_education_committee(self):
        return is_group_member(self, _('Education committee'))


class Relationship(models.Model):
    class Meta:
        verbose_name = _('Family relative')
        verbose_name_plural = _('Family relatives')

    relative = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="related_user",
                                 null=True, default=None, verbose_name=_('Parent'))
    child = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="child_user", null=True,
                              default=None, verbose_name=_('Child'))
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invited_user",
                                     null=True, default=None, verbose_name=_('Invited user'))

    WAITING = 'WT'
    APPROVED = 'AP'
    DECLINED = 'DC'

    REQUEST_STATUS = (
        (WAITING, _('Waiting')),
        (APPROVED, _('Approved')),
        (DECLINED, _('Declined'))
    )

    request = models.CharField(max_length=2, choices=REQUEST_STATUS, default=WAITING,
                               verbose_name=_('Relationship request'))

    def __str__(self):
        return _('Relationship #%(id)s') % {'id': self.id}
