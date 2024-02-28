# Generated by Django 4.2 on 2024-02-23 09:21

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0113_alter_edtversion_unique_together_remove_course_week_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseavailability',
            name='is_default',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='coursemodification',
            name='start_time_old',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='roomavailability',
            name='is_default',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='useravailability',
            name='is_default',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='coursestarttimeconstraint',
            name='allowed_start_times',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TimeField(), default=list, size=None),
        ),
    ]
