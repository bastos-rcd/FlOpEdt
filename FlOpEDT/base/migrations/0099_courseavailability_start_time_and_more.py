# Generated by Django 4.2 on 2024-02-15 08:53

import datetime
from django.db import migrations, models


def availability_date_and_time_to_datetime(apps, schema_editor):
    for AvailabilityModel in map(
        lambda m: apps.get_model("base", m),
        ["UserAvailability", "CourseAvailability", "RoomAvailability"],
    ):
        for av in AvailabilityModel.objects.all():
            av.start_time = datetime.datetime.combine(av.date, av.in_day_start_time)
            av.save()


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0098_rename_clean_day_courseavailability_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="courseavailability",
            name="start_time",
            field=models.DateTimeField(default=datetime.datetime(1871, 3, 18, 0, 0)),
        ),
        migrations.AddField(
            model_name="roomavailability",
            name="start_time",
            field=models.DateTimeField(default=datetime.datetime(1871, 3, 18, 0, 0)),
        ),
        migrations.AddField(
            model_name="useravailability",
            name="start_time",
            field=models.DateTimeField(default=datetime.datetime(1871, 3, 18, 0, 0)),
        ),
        migrations.RunPython(availability_date_and_time_to_datetime),
    ]