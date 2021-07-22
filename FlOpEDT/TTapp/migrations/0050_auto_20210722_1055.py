# Generated by Django 3.1.7 on 2021-07-22 10:55

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0081_auto_20210710_2236'),
        ('people', '0031_auto_20210709_0953'),
        ('TTapp', '0049_auto_20210710_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='limitholes',
            name='weeks',
            field=models.ManyToManyField(blank=True, to='base.Week'),
        ),
        migrations.CreateModel(
            name='LimitTutorTimePerWeeks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveSmallIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('modified_at', models.DateField(auto_now=True)),
                ('min_time_per_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('max_time_per_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('tolerated_margin', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100)])),
                ('number_of_weeks', models.PositiveSmallIntegerField(default=1, verbose_name='Number of weeks')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.department')),
                ('train_progs', models.ManyToManyField(blank=True, to='base.TrainingProgramme')),
                ('tutors', models.ManyToManyField(blank=True, to='people.Tutor')),
                ('weeks', models.ManyToManyField(blank=True, to='base.Week')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
