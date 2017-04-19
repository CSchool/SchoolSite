# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-19 14:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0033_auto_20170418_0931'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventapplication',
            name='confirm_participation',
        ),
        migrations.AlterField(
            model_name='eventapplication',
            name='issued_at',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Issued at'),
        ),
        migrations.AlterField(
            model_name='eventapplication',
            name='submitted_at',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Submitted at'),
        ),
    ]
