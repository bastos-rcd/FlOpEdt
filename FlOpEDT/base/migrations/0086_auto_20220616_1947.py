# Generated by Django 3.0.14 on 2022-06-16 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0085_auto_20220523_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='ppn',
            field=models.CharField(default='M', max_length=30),
        ),
    ]
