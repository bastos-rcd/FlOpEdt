# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-04 19:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('modif', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('TTapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stabilize',
            name='group',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.Group'),
        ),
        migrations.AddField(
            model_name='stabilize',
            name='module',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.Module'),
        ),
        migrations.AddField(
            model_name='stabilize',
            name='train_prog',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.TrainingProgramme'),
        ),
        migrations.AddField(
            model_name='stabilize',
            name='tutor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='simultaneouscourses',
            name='course1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course1', to='modif.Course'),
        ),
        migrations.AddField(
            model_name='simultaneouscourses',
            name='course2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course2', to='modif.Course'),
        ),
        migrations.AddField(
            model_name='reasonabledays',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.Group'),
        ),
        migrations.AddField(
            model_name='reasonabledays',
            name='train_prog',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.TrainingProgramme'),
        ),
        migrations.AddField(
            model_name='reasonabledays',
            name='tutor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='minnonpreferedslot',
            name='train_prog',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.TrainingProgramme'),
        ),
        migrations.AddField(
            model_name='minnonpreferedslot',
            name='tutor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='minhalfdays',
            name='module',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.Module'),
        ),
        migrations.AddField(
            model_name='minhalfdays',
            name='tutor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='limitnatureperperiod',
            name='module',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.Module'),
        ),
        migrations.AddField(
            model_name='limitnatureperperiod',
            name='train_prog',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.TrainingProgramme'),
        ),
        migrations.AddField(
            model_name='limitnatureperperiod',
            name='tutor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='avoidbothslots',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.Group'),
        ),
        migrations.AddField(
            model_name='avoidbothslots',
            name='slot1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slot1', to='modif.Slot'),
        ),
        migrations.AddField(
            model_name='avoidbothslots',
            name='slot2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slot2', to='modif.Slot'),
        ),
        migrations.AddField(
            model_name='avoidbothslots',
            name='train_prog',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.TrainingProgramme'),
        ),
        migrations.AddField(
            model_name='avoidbothslots',
            name='tutor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
