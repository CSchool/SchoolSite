# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-29 07:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0012_relationship_confirmation_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='valid_until',
            field=models.DateTimeField(default=None, null=True, verbose_name='Valid until'),
        ),
    ]