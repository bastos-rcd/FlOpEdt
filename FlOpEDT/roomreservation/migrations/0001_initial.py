# Generated by Django 3.0.14 on 2022-10-06 09:18

import colorfield.fields
from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0089_booleanroomattribute_booleanroomattributevalues_numericroomattribute_numericroomattributevalues_room'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReservationPeriodicity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(blank=True)),
                ('end', models.DateField(blank=True)),
                ('periodicity_type', models.CharField(choices=[('BW', 'By week'), ('EM', 'Each month at the same date'), ('BM', 'By Month')], default='BW', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='RoomReservationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('bg_color', colorfield.fields.ColorField(default='#95a5a6', max_length=18)),
            ],
        ),
        migrations.CreateModel(
            name='ReservationPeriodicityByMonth',
            fields=[
                ('periodicity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='BM', serialize=False, to='roomreservation.ReservationPeriodicity')),
                ('bm_x_choice', models.SmallIntegerField(blank=True, choices=[(1, 'First'), (2, 'Second'), (3, 'Third'), (4, 'Fourth'), (-2, 'Ante Last'), (-1, 'Last')], null=True)),
                ('bm_day_choice', models.CharField(blank=True, choices=[('m', 'monday'), ('tu', 'tuesday'), ('w', 'wednesday'), ('th', 'thursday'), ('f', 'friday'), ('sa', 'saturday'), ('su', 'sunday')], max_length=2, null=True)),
            ],
            bases=('roomreservation.reservationperiodicity',),
        ),
        migrations.CreateModel(
            name='ReservationPeriodicityByWeek',
            fields=[
                ('periodicity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='BW', serialize=False, to='roomreservation.ReservationPeriodicity')),
                ('bw_weekdays', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('m', 'monday'), ('tu', 'tuesday'), ('w', 'wednesday'), ('th', 'thursday'), ('f', 'friday'), ('sa', 'saturday'), ('su', 'sunday')], max_length=2), blank=True, null=True, size=None)),
                ('bw_weeks_interval', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
            bases=('roomreservation.reservationperiodicity',),
        ),
        migrations.CreateModel(
            name='ReservationPeriodicityEachMonthSameDate',
            fields=[
                ('periodicity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='EM', serialize=False, to='roomreservation.ReservationPeriodicity')),
            ],
            bases=('roomreservation.reservationperiodicity',),
        ),
        migrations.CreateModel(
            name='RoomReservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('description', models.TextField(blank=True, null=True)),
                ('email', models.BooleanField(default=False)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('periodicity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='roomreservation.ReservationPeriodicity')),
                ('reservation_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='roomreservation.RoomReservationType')),
                ('responsible', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservationResp', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservationRoom', to='base.Room')),
            ],
        ),
    ]
