# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-18 15:19
from __future__ import unicode_literals

from django.db import migrations, models
import main.validators


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0016_auto_20170114_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventapplication',
            name='phone',
            field=models.CharField(max_length=18, null=True, validators=[main.validators.PhoneValidator()], verbose_name='Phone number'),
        ),
    ]