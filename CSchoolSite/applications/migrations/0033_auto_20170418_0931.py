# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-18 06:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0032_auto_20170418_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventapplication',
            name='issued_at',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Issued'),
        ),
        migrations.AlterField(
            model_name='eventapplication',
            name='issued_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issued_applications', related_query_name='issued_application', to=settings.AUTH_USER_MODEL, verbose_name='Issued by'),
        ),
        migrations.AlterField(
            model_name='eventapplication',
            name='submitted_at',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Submitted'),
        ),
    ]
