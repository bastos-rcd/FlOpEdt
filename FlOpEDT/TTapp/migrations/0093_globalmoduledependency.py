# Generated by Django 4.2 on 2024-03-11 10:38

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0040_rename_max_hours_per_day_tutorpreference_max_time_per_day_and_more'),
        ('base', '0120_remove_dependency_nd'),
        ('TTapp', '0092_remove_breakaroundcoursetype_min_break_length_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalModuleDependency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveSmallIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('title', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('modified_at', models.DateField(auto_now=True)),
                ('day_gap', models.PositiveSmallIntegerField(default=0, verbose_name='Minimal day gap between courses')),
                ('course1_tutor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='global_dependency_course1_tutor', to='people.tutor')),
                ('course1_type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='global_dependency_course1_type', to='base.coursetype')),
                ('course2_tutor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='global_dependency_course2_tutor', to='people.tutor')),
                ('course2_type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='global_dependency_course2_type', to='base.coursetype')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.department')),
                ('groups', models.ManyToManyField(blank=True, related_name='global_dependency_groups', to='base.structuralgroup')),
                ('modules', models.ManyToManyField(blank=True, related_name='global_module_dependencies', to='base.module')),
                ('periods', models.ManyToManyField(blank=True, to='base.schedulingperiod')),
                ('train_progs', models.ManyToManyField(blank=True, to='base.trainingprogramme')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
