# Generated by Django 3.0.14 on 2023-12-06 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TTapp', '0078_auto_20231205_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='nogroupcourseonday',
            name='transversal_groups_included',
            field=models.BooleanField(default=True, verbose_name='transveral_groups_included'),
        ),
    ]