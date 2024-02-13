# Generated by Django 4.2 on 2024-02-13 08:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("base", "0094_rename_coursepreference_courseavailability_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useravailability",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
