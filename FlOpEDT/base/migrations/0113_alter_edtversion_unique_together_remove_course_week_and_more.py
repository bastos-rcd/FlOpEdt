# Generated by Django 4.2 on 2024-02-23 07:35

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import datetime as dt
from base.timing import days_index

def convert_week_to_scheduling_period(apps, schema_editor, model_name, app_name='base'):
    Model = apps.get_model(app_name, model_name)
    SchedulingPeriod = apps.get_model('base', 'SchedulingPeriod')
    for obj in Model.objects.all():
        week = obj.week
        if obj.week.year < 2023:
            continue
        monday = dt.date.fromisocalendar(week.year, week.nb , 1)
        scheduling_period = SchedulingPeriod.objects.get(start_date=monday, mode="w")
        obj.period = scheduling_period
        obj.save()

def convert_week_to_scheduling_period_edtversion(apps, schema_editor):
    convert_week_to_scheduling_period(apps, schema_editor, 'EdtVersion')

def convert_week_to_scheduling_period_course(apps, schema_editor):
    convert_week_to_scheduling_period(apps, schema_editor, 'Course')

def convert_week_to_scheduling_period_regen(apps, schema_editor):
    convert_week_to_scheduling_period(apps, schema_editor, 'Regen')

def convert_week_day_into_date(apps, schema_editor, model_name, app_name='base'):
    Model = apps.get_model(app_name, model_name)
    for obj in Model.objects.all():
        week = obj.week
        day = obj.day
        date = dt.date.fromisocalendar(week.year if week.year>0 else 1, week.nb if week.nb>0 else 1, days_index[day]+1 % 7)
        obj.date = date
        obj.save()

def convert_week_day_into_date_holiday(apps, schema_editor):
    convert_week_day_into_date(apps, schema_editor, 'Holiday')

def convert_day_start_time_into_new_start_time(apps, schema_editor):
    ScheduledCourse = apps.get_model('base', 'ScheduledCourse')
    for sc in ScheduledCourse.objects.all():
        new_date_time = dt.datetime.combine(sc.course.period.start_date,dt.time(0)) + dt.timedelta(days=days_index[sc.day]) + dt.timedelta(minutes=sc.start_time)
        sc.start_time_tmp = new_date_time
        sc.save()





class Migration(migrations.Migration):

    dependencies = [
        ('TTapp', '0079_remove_assignallcourses_weeks_and_more'),
        ('people', '0038_remove_physicalpresence_day_and_more'),
        ('base', '0112_remove_timegeneralsettings_default_availability_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.schedulingperiod'),
        ),
        migrations.RunPython(convert_week_to_scheduling_period_course),
        migrations.AddField(
            model_name='coursemodification',
            name='old_period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.schedulingperiod'),
        ),
        migrations.AddField(
            model_name='edtversion',
            name='period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.schedulingperiod'),
        ),
        migrations.RunPython(convert_week_to_scheduling_period_edtversion),
        migrations.AddField(
            model_name='groupcost',
            name='period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.schedulingperiod'),
        ),
        migrations.AddField(
            model_name='groupfreehalfday',
            name='period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.schedulingperiod'),
        ),
        migrations.AddField(
            model_name='holiday',
            name='date',
            field=models.DateField(default=datetime.date(1890, 5, 1)),
        ),
        migrations.RunPython(convert_week_day_into_date_holiday),
        migrations.AddField(
            model_name='moduletutorrepartition',
            name='scheduling_period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.schedulingperiod'),
        ),
        migrations.AddField(
            model_name='regen',
            name='period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.schedulingperiod'),
        ),
        migrations.RunPython(convert_week_to_scheduling_period_regen),
        migrations.AddField(
            model_name='schedulingperiod',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='traininghalfday',
            name='date',
            field=models.DateField(default=datetime.date(1890, 5, 1)),
        ),
        migrations.AddField(
            model_name='trainingperiod',
            name='periods',
            field=models.ManyToManyField(to='base.schedulingperiod'),
        ),
        migrations.AddField(
            model_name='tutorcost',
            name='period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.schedulingperiod'),
        ),
        migrations.AlterUniqueTogether(
            name='edtversion',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='course',
            name='week',
        ),
        migrations.RemoveField(
            model_name='coursemodification',
            name='old_week',
        ),
        migrations.RemoveField(
            model_name='groupcost',
            name='week',
        ),
        migrations.RemoveField(
            model_name='groupfreehalfday',
            name='week',
        ),
        migrations.RemoveField(
            model_name='holiday',
            name='day',
        ),
        migrations.RemoveField(
            model_name='holiday',
            name='week',
        ),
        migrations.RemoveField(
            model_name='moduletutorrepartition',
            name='week',
        ),
        migrations.RemoveField(
            model_name='regen',
            name='week',
        ),
        migrations.RemoveField(
            model_name='traininghalfday',
            name='day',
        ),
        migrations.RemoveField(
            model_name='traininghalfday',
            name='week',
        ),
        migrations.RemoveField(
            model_name='trainingperiod',
            name='ending_week',
        ),
        migrations.RemoveField(
            model_name='trainingperiod',
            name='starting_week',
        ),
        migrations.RemoveField(
            model_name='tutorcost',
            name='week',
        ),
        migrations.RemoveField(
            model_name='coursemodification',
            name='start_time_old',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='coursestarttimeconstraint',
            name='allowed_start_times',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TimeField(), default=[datetime.time(8, 0)], size=None),
        ),
        migrations.AddField(
            model_name='scheduledcourse',
            name='start_time_tmp',
            field=models.DateTimeField(null=True, default=None),
        ),
        migrations.RunPython(convert_day_start_time_into_new_start_time),
        migrations.RemoveField(
            model_name='scheduledcourse',
            name='start_time',
        ),
        migrations.RenameField(
            model_name='scheduledcourse',
            old_name='start_time_tmp',
            new_name='start_time',
        ),
        migrations.AlterField(
            model_name='scheduledcourse',
            name='start_time',
            field=models.DateTimeField(),
        ),
        migrations.RemoveField(
            model_name='scheduledcourse',
            name='day',
        ),
        migrations.AlterField(
            model_name='transversalgroup',
            name='parallel_groups',
            field=models.ManyToManyField(blank=True, to='base.transversalgroup'),
        ),
        migrations.AlterUniqueTogether(
            name='edtversion',
            unique_together={('department', 'period')},
        ),
        migrations.RemoveField(
            model_name='edtversion',
            name='week',
        ),
        migrations.DeleteModel(
            name='Week',
        ),
    ]
