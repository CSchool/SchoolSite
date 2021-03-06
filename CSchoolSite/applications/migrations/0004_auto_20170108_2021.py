# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-08 17:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applications', '0003_event_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('TG', 'Тестируется'), ('TS', 'Тестирование пройдено'), ('ST', 'Обучается'), ('SC', 'Успешно окончил(а)'), ('FL', 'Неуспешно окончил(а)'), ('DQ', 'Исключён(а)')], default='TG', max_length=2, verbose_name='Статус заявки')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Заявка на событие',
                'verbose_name_plural': 'Заявки на события',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='users',
            field=models.ManyToManyField(through='applications.EventApplication', to=settings.AUTH_USER_MODEL),
        ),
    ]
