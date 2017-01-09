from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Period(models.Model):
    class Meta:
        verbose_name = _('Period')
        verbose_name_plural = _('Periods')
        permissions = (
            ("view_period", _("view periods")),
        )
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    begin = models.DateTimeField(verbose_name=_('Period begins'))
    end = models.DateTimeField(verbose_name=_('Period ends'))
    registration_begin = models.DateTimeField(verbose_name=_('Registration begins'))
    registration_end = models.DateTimeField(verbose_name=_('Registration ends'))

    def __str__(self):
        return self.name

    @property
    def registration_open(self):
        if self.registration_begin <= timezone.now() <= self.registration_end:
            return True
        return False

    @property
    def registration_started(self):
        if self.registration_begin <= timezone.now():
            return True
        return False

    @property
    def ongoing(self):
        if self.begin <= timezone.now() <= self.end:
            return True
        return False

    @property
    def began(self):
        if self.begin <= timezone.now():
            return True
        return False

    @property
    def ended(self):
        if timezone.now() > self.end:
            return True
        return False


class CampVoucher(models.Model):
    class Meta:
        verbose_name = _('Camp voucher')
        verbose_name_plural = _('Camp vouchers')
        permissions = (
            ("view_campvoucher", _("view camp vouchers")),
        )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Voucher owner'))
    period = models.ForeignKey('Period', on_delete=models.CASCADE, verbose_name=_('Period'))
    voucher_id = models.CharField(max_length=30, verbose_name=_('Voucher ID'))

    # Voucher status
    AWAITING_PAYMENT = 'WP'
    DECLINED = 'DC'
    PAID = 'PD'
    APPROVED = 'AP'

    CAMP_VOUCHER_STATUS_CHOICES = (
        (AWAITING_PAYMENT, _('Awaiting payment')),
        (DECLINED, _('Declined')),
        (PAID, _('Paid')),
        (APPROVED, _('Approved'))
    )

    status = models.CharField(max_length=2, choices=CAMP_VOUCHER_STATUS_CHOICES, default=AWAITING_PAYMENT, verbose_name='Статус')

    def __str__(self):
        return self.voucher_id


class Event(models.Model):
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    period = models.ForeignKey('Period', on_delete=models.CASCADE, verbose_name=_('Period'))
    users = models.ManyToManyField(User, through='EventApplication')
    description = models.TextField(verbose_name=_('Description'))
    begin = models.DateTimeField(verbose_name=_('Event begins'))
    end = models.DateTimeField(verbose_name=_('Event ends'))
    registration_begin = models.DateTimeField(verbose_name=_('Registration begins'))
    registration_end = models.DateTimeField(verbose_name=_('Registration ends'))
    is_open = models.BooleanField(verbose_name=_('Registration open'))
    limit = models.IntegerField(verbose_name=_('Participants limit'))

    # Event type
    CLASS_GROUP = 'CL'
    CAMP_GROUP = 'CA'
    OLYMP = 'OL'

    EVENT_TYPE_CHOICES = (
        (CLASS_GROUP, _('Class group')),
        (CAMP_GROUP, _('Camp group')),
        (OLYMP, _('Tournament'))
    )

    type = models.CharField(max_length=2, choices=EVENT_TYPE_CHOICES, default=CLASS_GROUP, verbose_name=_('Event type'))

    def __str__(self):
        return self.name

    @property
    def registration_open(self):
        if self.registration_begin <= timezone.now() <= self.registration_end and self.is_open:
            return True
        return False


class EventApplication(models.Model):
    class Meta:
        verbose_name = _('Event application')
        verbose_name_plural = _('Event applications')
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)

    # Registration status
    TESTING = 'TG'
    TESTING_SUCCEEDED = 'TS'
    STUDYING = 'ST'
    SUCCESSED = 'SC'
    FAILED = 'FL'
    DISQUALIFIED = 'DQ'

    EVENT_APPLICATION_STATUS_CHOICES = (
        (TESTING, _('Testing')),
        (TESTING_SUCCEEDED, _('Testing succeeded')),
        (STUDYING, _('Studying')),
        (SUCCESSED, _('Successed')),
        (FAILED, _('Failed')),
        (DISQUALIFIED, _('Disqualified'))
    )

    status = models.CharField(max_length=2, choices=EVENT_APPLICATION_STATUS_CHOICES, default=TESTING, verbose_name=_('Application status'))
