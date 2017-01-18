from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


# Create your models here.

class User(AbstractUser):
    patronymic = models.CharField(_('patronymic'), max_length=30, null=True, blank=True)
    birthday = models.DateField(_('birthday'), null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=16, null=True, blank=True)
