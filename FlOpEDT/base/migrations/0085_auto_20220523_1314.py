# Generated by Django 3.0.14 on 2022-05-23 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0084_roomponderation_basic_rooms'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='pay_module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses_as_pay_module', to='base.Module'),
        ),
        migrations.AddField(
            model_name='coursetype',
            name='pay_duration',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='modulesupp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses_as_modulesupp', to='base.Module'),
        ),
    ]
