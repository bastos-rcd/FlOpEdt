# Generated by Django 2.1.15 on 2020-04-17 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0053_auto_20200417_2102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='group',
        ),
    ]