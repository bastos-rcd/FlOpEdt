# Generated by Django 4.2 on 2024-02-26 03:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TTapp', '0082_alter_avoidbothtimessameday_time1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='breakaroundcoursetype',
            name='min_break_length',
        ),
        migrations.AddField(
            model_name='breakaroundcoursetype',
            name='min_break_length',
            field=models.DurationField(default=datetime.timedelta(seconds=900)),
        ),
    ]
