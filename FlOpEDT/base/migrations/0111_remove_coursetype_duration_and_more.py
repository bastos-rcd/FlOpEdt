# Generated by Django 4.2 on 2024-02-21 08:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0110_auto_20240221_1158"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="coursetype",
            name="duration",
        ),
        migrations.RemoveField(
            model_name="coursetype",
            name="pay_duration",
        ),
        migrations.AlterField(
            model_name="course",
            name="duration",
            field=models.DurationField(),
        ),
    ]