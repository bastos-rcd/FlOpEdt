# Generated by Django 4.2 on 2024-02-28 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0117_alter_schedulingperiod_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingperiod',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='training_periods', to='base.department'),
        ),
    ]