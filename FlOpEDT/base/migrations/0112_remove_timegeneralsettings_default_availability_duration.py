# Generated by Django 3.0.14 on 2024-02-21 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0111_remove_coursetype_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timegeneralsettings',
            name='default_availability_duration',
        ),
    ]