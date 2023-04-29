# Generated by Django 3.0.14 on 2023-04-27 10:07

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0036_notificationspreferences_notify_other_user_modifications'),
        ('base', '0091_auto_20221124_2149'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'verbose_name': 'course', 'verbose_name_plural': 'courses'},
        ),
        migrations.AlterModelOptions(
            name='coursetype',
            options={'verbose_name': 'course type', 'verbose_name_plural': 'course types'},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={'verbose_name': 'department', 'verbose_name_plural': 'departments'},
        ),
        migrations.AlterModelOptions(
            name='dependency',
            options={'verbose_name': 'Depedency', 'verbose_name_plural': 'Dependencies'},
        ),
        migrations.AlterModelOptions(
            name='genericgroup',
            options={'verbose_name': 'generic group', 'verbose_name_plural': 'generic groups'},
        ),
        migrations.AlterModelOptions(
            name='grouptype',
            options={'verbose_name': 'group type', 'verbose_name_plural': 'groupe types'},
        ),
        migrations.AlterModelOptions(
            name='holiday',
            options={'verbose_name': 'holiday', 'verbose_name_plural': 'holidays'},
        ),
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ['abbrev'], 'verbose_name': 'module', 'verbose_name_plural': 'modules'},
        ),
        migrations.AlterModelOptions(
            name='period',
            options={'verbose_name': 'period', 'verbose_name_plural': 'periods'},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'verbose_name': 'room', 'verbose_name_plural': 'rooms'},
        ),
        migrations.AlterModelOptions(
            name='roomtype',
            options={'verbose_name': 'room type', 'verbose_name_plural': 'room types'},
        ),
        migrations.AlterModelOptions(
            name='scheduledcourse',
            options={'verbose_name': 'scheduled course', 'verbose_name_plural': 'scheduled courses'},
        ),
        migrations.AlterModelOptions(
            name='structuralgroup',
            options={'verbose_name': 'structural group', 'verbose_name_plural': 'structural groups'},
        ),
        migrations.AlterModelOptions(
            name='trainingprogramme',
            options={'verbose_name': 'training programme', 'verbose_name_plural': 'training programmes'},
        ),
        migrations.AlterModelOptions(
            name='transversalgroup',
            options={'verbose_name': 'transversal group', 'verbose_name_plural': 'transversal groups'},
        ),
        migrations.AlterModelOptions(
            name='week',
            options={'verbose_name': 'week', 'verbose_name_plural': 'weeks'},
        ),
        migrations.AlterField(
            model_name='holiday',
            name='day',
            field=models.CharField(choices=[('m', 'Monday'), ('tu', 'Tuesday'), ('w', 'Wednesday'), ('th', 'Thursday'), ('f', 'Friday'), ('sa', 'Saturday'), ('su', 'Sunday')], default='m', max_length=2),
        ),
        migrations.AlterField(
            model_name='module',
            name='abbrev',
            field=models.CharField(max_length=100, verbose_name='abbreviation'),
        ),
        migrations.AlterField(
            model_name='module',
            name='head',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='people.Tutor', verbose_name='head (resp)'),
        ),
        migrations.AlterField(
            model_name='module',
            name='name',
            field=models.CharField(max_length=200, null=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='module',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Period', verbose_name='period'),
        ),
        migrations.AlterField(
            model_name='module',
            name='train_prog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.TrainingProgramme', verbose_name='training programme'),
        ),
        migrations.AlterField(
            model_name='timegeneralsettings',
            name='days',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('m', 'Monday'), ('tu', 'Tuesday'), ('w', 'Wednesday'), ('th', 'Thursday'), ('f', 'Friday'), ('sa', 'Saturday'), ('su', 'Sunday')], max_length=2), size=None),
        ),
        migrations.AlterField(
            model_name='traininghalfday',
            name='day',
            field=models.CharField(choices=[('m', 'Monday'), ('tu', 'Tuesday'), ('w', 'Wednesday'), ('th', 'Thursday'), ('f', 'Friday'), ('sa', 'Saturday'), ('su', 'Sunday')], default='m', max_length=2),
        ),
    ]
