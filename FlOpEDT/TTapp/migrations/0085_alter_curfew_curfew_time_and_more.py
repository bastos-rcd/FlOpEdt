# Generated by Django 4.2 on 2024-02-26 08:39

from django.db import migrations, models
import datetime as dt

class Migration(migrations.Migration):

    dependencies = [
        ('TTapp', '0084_alter_limitundesiredslotsperperiod_slot_end_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curfew',
            name='curfew_time',
        ),
        migrations.RemoveField(
            model_name='limitundesiredslotsperperiod',
            name='slot_end_time',
        ),
        migrations.RemoveField(
            model_name='limitundesiredslotsperperiod',
            name='slot_start_time',
        ),
        migrations.AddField(
            model_name='curfew',
            name='curfew_time',
            field=models.TimeField(),
        ),
        migrations.AddField(
            model_name='limitundesiredslotsperperiod',
            name='slot_end_time',
            field=models.TimeField(),
        ),
        migrations.AddField(
            model_name='limitundesiredslotsperperiod',
            name='slot_start_time',
            field=models.TimeField(),
        )
    ]