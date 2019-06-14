# Generated by Django 2.1.3 on 2018-11-18 14:20

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_timegeneralsettings_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timegeneralsettings',
            name='days',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('m', 'monday'), ('tu', 'tuesday'), ('w', 'wednesday'), ('th', 'thursday'), ('f', 'friday'), ('sa', 'saturday'), ('su', 'sunday')], max_length=2), size=None),
        ),
    ]