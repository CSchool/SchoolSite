# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 18:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0015_TelegramIntegration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationship',
            name='confirmation_code',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=8, null=True, verbose_name='Confirmation code'),
        ),
        migrations.AlterField(
            model_name='relationship',
            name='valid_until',
            field=models.DateTimeField(blank=True, db_index=True, default=None, null=True, verbose_name='Valid until'),
        ),
    ]
