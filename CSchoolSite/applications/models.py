from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Period(models.Model):
    class Meta:
        verbose_name = 'Период обучения'
        verbose_name_plural = 'Периоды обучения'
    name = models.CharField(max_length=100, verbose_name='Название')
    begin = models.DateTimeField(verbose_name='Начало обучения')
    end = models.DateTimeField(verbose_name='Окончание обучения')
    registration_begin = models.DateTimeField(verbose_name='Начало регистрации')
    registration_end = models.DateTimeField(verbose_name='Окончание регистрации')

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
        verbose_name = 'Путёвка'
        verbose_name_plural = 'Путёвки'
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец путёвки')
    period = models.ForeignKey('Period', on_delete=models.CASCADE, verbose_name='Смена')
    voucher_id = models.CharField(max_length=30, verbose_name='Номер путёвки')

    # Voucher status
    AWAITING_PAYMENT = 'WP'
    DECLINED = 'DC'
    PAID = 'PD'
    APPROVED = 'AP'

    CAMP_VOUCHER_STATUS_CHOICES = (
        (AWAITING_PAYMENT, 'Ожидает оплаты'),
        (DECLINED, 'Отклонено'),
        (PAID, 'Оплачено'),
        (APPROVED, 'Подтверждено')
    )

    status = models.CharField(max_length=2, choices=CAMP_VOUCHER_STATUS_CHOICES, default=AWAITING_PAYMENT, verbose_name='Статус')

    def __str__(self):
        return self.voucher_id


class Event(models.Model):
    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
    name = models.CharField(max_length=100, verbose_name='Название')
    period = models.ForeignKey('Period', on_delete=models.CASCADE, verbose_name='Период')
    users = models.ManyToManyField(User, through='EventApplication')
    description = models.TextField(verbose_name='Описание')
    begin = models.DateTimeField(verbose_name='Начало события')
    end = models.DateTimeField(verbose_name='Окончание события')
    registration_begin = models.DateTimeField(verbose_name='Начало регистрации')
    registration_end = models.DateTimeField(verbose_name='Окончание регистрации')
    is_open = models.BooleanField(verbose_name='Регистрация открыта')
    limit = models.IntegerField(verbose_name='Максимальное количество участников')

    # Event type
    CLASS_GROUP = 'CL'
    CAMP_GROUP = 'CA'
    OLYMP = 'OL'

    EVENT_TYPE_CHOICES = (
        (CLASS_GROUP, 'Учебная группа'),
        (CAMP_GROUP, 'Отряд'),
        (OLYMP, 'Турнир')
    )

    type = models.CharField(max_length=2, choices=EVENT_TYPE_CHOICES, default=CLASS_GROUP, verbose_name='Тип события')

    def __str__(self):
        return self.name

    @property
    def registration_open(self):
        if self.registration_begin <= timezone.now() <= self.registration_end and self.is_open:
            return True
        return False


class EventApplication(models.Model):
    class Meta:
        verbose_name = "Заявка на событие"
        verbose_name_plural = "Заявки на события"
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
        (TESTING, "Тестируется"),
        (TESTING_SUCCEEDED, "Тестирование пройдено"),
        (STUDYING, "Обучается"),
        (SUCCESSED, "Успешно окончил(а)"),
        (FAILED, "Неуспешно окончил(а)"),
        (DISQUALIFIED, "Исключён(а)")
    )

    status = models.CharField(max_length=2, choices=EVENT_APPLICATION_STATUS_CHOICES, default=TESTING, verbose_name='Статус заявки')