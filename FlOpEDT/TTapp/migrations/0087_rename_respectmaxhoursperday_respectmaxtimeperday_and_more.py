# Generated by Django 4.2 on 2024-02-26 15:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0116_rename_period_module_training_period'),
        ('people', '0040_rename_max_hours_per_day_tutorpreference_max_time_per_day_and_more'),
        ('TTapp', '0086_alter_groupsminhoursperday_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RespectMaxHoursPerDay',
            new_name='RespectMaxTimePerDay',
        ),
        migrations.RenameModel(
            old_name='RespectTutorsMinHoursPerDay',
            new_name='RespectTutorsMinTimePerDay',
        ),
        migrations.AlterModelOptions(
            name='respectmaxtimeperday',
            options={'verbose_name': 'Respect max time per days bounds', 'verbose_name_plural': 'Respect max time per days bounds'},
        ),
        migrations.AlterModelOptions(
            name='respecttutorsmintimeperday',
            options={'verbose_name': 'Respect tutors min time per day bounds', 'verbose_name_plural': 'Respect tutors min time per day bounds'},
        ),
    ]
