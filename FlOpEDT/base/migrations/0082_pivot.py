# Generated by Django 3.1.7 on 2021-08-25 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0080_dependency_day_gap'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pivot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ND', models.BooleanField(default=False, verbose_name='On different days')),
                ('other_courses', models.ManyToManyField(related_name='as_pivot_other', to='base.Course')),
                ('pivot_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='as_pivot', to='base.course')),
            ],
        ),
    ]