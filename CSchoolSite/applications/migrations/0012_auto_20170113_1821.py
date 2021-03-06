# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-13 15:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applications', '0011_auto_20170112_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='TheoryExam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rand_questions', models.IntegerField(verbose_name='Random questions')),
                ('slot_questions', models.IntegerField(verbose_name='Slot questions')),
                ('min_score', models.IntegerField(verbose_name='Minimum total score')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='applications.Event')),
            ],
            options={
                'verbose_name': 'Theory exam',
                'verbose_name_plural': 'Theory exams',
            },
        ),
        migrations.CreateModel(
            name='TheoryExamApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TheoryExamApplicationQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField()),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.TheoryExamApplication')),
            ],
            options={
                'ordering': ('index',),
            },
        ),
        migrations.CreateModel(
            name='TheoryExamQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=500, verbose_name='Question')),
                ('answer', models.CharField(max_length=100, verbose_name='Answer')),
                ('trim_answer', models.BooleanField(default=True, verbose_name='Remove extra spaces from answer')),
                ('case_sensitive_answer', models.BooleanField(default=False, verbose_name='Answer is case-sensitive')),
                ('slot', models.IntegerField(verbose_name='Question slot')),
                ('qtype', models.CharField(choices=[('NB', 'Integer number as an answer'), ('TX', 'String as an answer'), ('CH', 'One option as an answer'), ('MC', 'Several options as an answer')], default='TX', max_length=2, verbose_name='Answer type')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.TheoryExam')),
            ],
            options={
                'verbose_name': 'Theory exam question',
                'verbose_name_plural': 'Theory exams questions',
            },
        ),
        migrations.CreateModel(
            name='TheoryExamQuestionOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.CharField(max_length=100, verbose_name='Possible answer')),
                ('short', models.CharField(max_length=15, verbose_name='Short ID')),
                ('correct', models.BooleanField(verbose_name='This answer is correct')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.TheoryExamQuestion')),
            ],
            options={
                'verbose_name': 'Possible answer',
                'verbose_name_plural': 'Possible answers',
                'ordering': ('short',),
            },
        ),
        migrations.AddField(
            model_name='theoryexamapplicationquestion',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.TheoryExamQuestion'),
        ),
        migrations.AddField(
            model_name='theoryexamapplication',
            name='questions',
            field=models.ManyToManyField(through='applications.TheoryExamApplicationQuestion', to='applications.TheoryExamQuestion'),
        ),
        migrations.AddField(
            model_name='theoryexamapplication',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventapplication',
            name='theory_exam',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='applications.TheoryExamApplication'),
        ),
    ]
