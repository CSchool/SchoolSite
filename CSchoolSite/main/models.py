from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    patronymic = models.CharField(_('patronymic'), max_length=30, null=True, blank=True)
    birthday = models.DateField(_('birthday'), null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=16, null=True, blank=True)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
