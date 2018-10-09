# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-07 07:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0016_auto_20170503_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notify_email',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='notify_onsite',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='notify_telegram',
            field=models.BooleanField(default=True),
        ),
    ]