# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-11 17:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'UserProfile', 'verbose_name_plural': 'UserProfile'},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='birthday'),
        ),
    ]
