# Generated by Django 4.2 on 2024-02-13 08:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0036_notificationspreferences_notify_other_user_modifications"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="first name"
            ),
        ),
    ]
