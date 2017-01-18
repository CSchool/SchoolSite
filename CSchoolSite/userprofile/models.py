from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
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
