# Generated by Django 3.0.14 on 2022-12-19 11:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0091_auto_20221124_2149'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('roomreservation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomReservationValidationEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.Room')),
                ('validators', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
