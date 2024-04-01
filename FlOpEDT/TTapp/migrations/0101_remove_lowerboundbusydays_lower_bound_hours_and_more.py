# Generated by Django 4.2 on 2024-04-01 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "people",
            "0040_rename_max_hours_per_day_tutorpreference_max_time_per_day_and_more",
        ),
        ("TTapp", "0100_remove_limitcoursetypetimeperperiod_max_hours_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lowerboundbusydays",
            name="lower_bound_hours",
        ),
        migrations.RemoveField(
            model_name="lowerboundbusydays",
            name="tutor",
        ),
        migrations.AddField(
            model_name="lowerboundbusydays",
            name="lower_bound_time",
            field=models.DurationField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lowerboundbusydays",
            name="tutors",
            field=models.ManyToManyField(to="people.tutor"),
        ),
        migrations.AlterField(
            model_name="parallelizecourses",
            name="desired_busy_slots_duration",
            field=models.DurationField(verbose_name="Desired busy slots duration"),
        ),
    ]
