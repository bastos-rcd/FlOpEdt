# Generated by Django 3.0.14 on 2022-08-09 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0035_auto_20220809_1553'),
        ('TTapp', '0063_auto_20220723_1112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='minimizebusydays',
            options={'verbose_name': 'Minimize tutors busy days', 'verbose_name_plural': 'Minimize tutors busy days'},
        ),
        migrations.AlterField(
            model_name='mintutorshalfdays',
            name='tutors',
            field=models.ManyToManyField(blank=True, to='people.Tutor', verbose_name='tutors'),
        ),
    ]
