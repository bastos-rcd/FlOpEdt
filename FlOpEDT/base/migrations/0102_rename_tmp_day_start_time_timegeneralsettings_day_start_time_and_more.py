# Generated by Django 4.2 on 2024-02-20 09:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0101_remove_timegeneralsettings_day_finish_time_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="timegeneralsettings",
            old_name="tmp_day_start_time",
            new_name="day_start_time",
        ),
        migrations.RenameField(
            model_name="timegeneralsettings",
            old_name="tmp_default_preference_duration",
            new_name="default_availability_duration",
        ),
    ]