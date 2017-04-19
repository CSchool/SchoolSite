# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-19 15:19
from __future__ import unicode_literals

import applications.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0034_auto_20170419_1739'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('file', models.FileField(upload_to=applications.models.PeriodAttachment.get_upload_path, verbose_name='File')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.Period', verbose_name='Period')),
            ],
            options={
                'verbose_name_plural': 'Attachments',
                'verbose_name': 'Attachment',
            },
        ),
    ]
