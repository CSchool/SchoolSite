# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-04 14:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0017_auto_20170118_1819'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='begin',
        ),
        migrations.RemoveField(
            model_name='event',
            name='end',
        ),
        migrations.RemoveField(
            model_name='event',
            name='registration_begin',
        ),
        migrations.RemoveField(
            model_name='event',
            name='registration_end',
        ),
    ]
