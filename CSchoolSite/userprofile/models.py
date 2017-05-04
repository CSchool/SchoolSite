from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import signing

from CSchoolSite import settings
from main.validators import PhoneValidator

from applications.models import Period
from userprofile.utils import is_group_member
from django.utils import baseconv


class User(AbstractUser):
    patronymic = models.CharField(_('patronymic'), max_length=30, null=True, blank=True, default='')
    birthday = models.DateField(_('birthday'), null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=18, null=True, blank=True, default='',
                             validators=[PhoneValidator()], help_text=_('The format of phone numbers is +7 (123) 456-78-90'))

    personal = models.BooleanField(_('Account is personal'), null=False, blank=False, default=True,
                                   help_text=_("Enable user profile and social/personal actions"))

    alias = models.CharField(_('Alias'), max_length=250, null=True, blank=True, default='',
                             help_text=_('Use contents of this field instead of username'))

    telegram_id = models.BigIntegerField(null=True, blank=True, default=None, unique=True)
    telegram_username = models.CharField(max_length=256, default=None, unique=True, blank=True, null=True)

    def __str__(self):
        if not self.email:
            return self.get_aliased_username()
        return '{name} <{email}>'.format(name=self.get_aliased_username(), email=self.email)

    def get_initials(self):
        full_name = '%s %s %s' % (self.last_name or '', self.first_name or '', self.patronymic or '')
        return full_name.strip()

    def get_aliased_username(self):
        return self.alias if self.alias else self.get_initials()

    def is_eligible_for_application(self, period=None):
        if not self.is_authenticated():
            return False
        if not self.personal:
            return False
        if not self.is_parent:
            return False
        if period:
            return period.registration_open
        return bool(Period.objects.filter(registration_begin__lt=timezone.now(), registration_end__gt=timezone.now()))

    def is_eligible_for_application_viewing(self):
        if not self.is_authenticated():
            return False
        if not self.personal:
            return False
        return bool(Period.objects.filter(registration_begin__lt=timezone.now(), registration_end__gt=timezone.now()))

    def get_telegram_deeplink(self):
        try:
            from telegram.bot import digest
            return '{}_{}'.format(self.id, digest(self.id))
        except:
            return ''

    @property
    def is_parent(self):
        if hasattr(self, '_cached_is_parent'):
            return getattr(self, '_cached_is_parent', False)
        else:
            res = Relationship.objects.filter(relative=self, request=Relationship.APPROVED).exists()
            setattr(self, '_cached_is_parent', res)
            return res
        # return is_group_member(self, _('Parents'))

    @property
    def is_student(self):
        return not self.is_parent and not self.is_education_committee
        # return is_group_member(self, _('Students'))

    @property
    def is_education_committee(self):
        return is_group_member(self, _('Education committee'))


class Relationship(models.Model):
    class Meta:
        verbose_name = _('Family relative')
        verbose_name_plural = _('Family relatives')

    relative = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="related_user",
                                 null=True, default=None, blank=True, verbose_name=_('Parent'))
    child = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="child_user", null=True,
                              default=None, blank=True, verbose_name=_('Child'))
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invited_user",
                                     null=True, default=None, blank=True, verbose_name=_('Invited user'))

    confirmation_code = models.CharField(db_index=True, max_length=8, blank=True, default=None, null=True, verbose_name=_('Confirmation code'))
    valid_until = models.DateTimeField(db_index=True, default=None, blank=True, null=True, verbose_name=_('Valid until'))

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
