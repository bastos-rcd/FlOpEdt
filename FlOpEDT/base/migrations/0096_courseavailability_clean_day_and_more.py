# Generated by Django 4.2 on 2024-02-13 14:31

import datetime
from django.db import migrations, models

from base.timing import Day


def availability_floptime_to_datetime(apps, schema_editor):
    for AvailabilityModel in map(
        lambda m: apps.get_model("base", m),
        ["UserAvailability", "CourseAvailability", "RoomAvailability"],
    ):
        to_be_removed = []
        for av in AvailabilityModel.objects.all():
            av.clean_day_time = datetime.time(
                hour=av.start_time // 60, minute=av.start_time % 60
            )
            day_number = [d[0] for d in Day.CHOICES].index(av.day) + 1
            if av.week is not None:
                try:
                    av.clean_day = datetime.date.fromisocalendar(
                        av.week.year, av.week.nb, day_number
                    )
                except ValueError:
                    to_be_removed.append(av.id)
            else:
                av.clean_day = datetime.date(1, 1, day_number)
            av.clean_duration = datetime.timedelta(minutes=av.duration)
            av.save()
        AvailabilityModel.objects.filter(id__in=to_be_removed).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0095_alter_useravailability_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="courseavailability",
            name="clean_day",
            field=models.DateField(default=datetime.date(1, 1, 1)),
        ),
        migrations.AddField(
            model_name="courseavailability",
            name="clean_day_time",
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
        migrations.AddField(
            model_name="courseavailability",
            name="clean_duration",
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AddField(
            model_name="roomavailability",
            name="clean_day",
            field=models.DateField(default=datetime.date(1, 1, 1)),
        ),
        migrations.AddField(
            model_name="roomavailability",
            name="clean_day_time",
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
        migrations.AddField(
            model_name="roomavailability",
            name="clean_duration",
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AddField(
            model_name="useravailability",
            name="clean_day",
            field=models.DateField(default=datetime.date(1, 1, 1)),
        ),
        migrations.AddField(
            model_name="useravailability",
            name="clean_day_time",
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
        migrations.AddField(
            model_name="useravailability",
            name="clean_duration",
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.RunPython(availability_floptime_to_datetime),
    ]
