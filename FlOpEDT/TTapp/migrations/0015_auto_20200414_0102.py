# Generated by Django 2.1.15 on 2020-04-14 01:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TTapp', '0014_auto_20200408_1350'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='minimizebusydays',
            options={'verbose_name_plural': 'Minimize busy days'},
        ),
        migrations.AlterModelOptions(
            name='respectboundperday',
            options={'verbose_name_plural': 'Respecter les limites horaires'},
        ),
        migrations.AlterModelOptions(
            name='simultaneouscourses',
            options={'verbose_name_plural': 'Simultaneous courses'},
        ),
    ]
