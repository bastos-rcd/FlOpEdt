# Generated by Django 4.2 on 2024-03-15 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0125_remove_groupcost_work_copy_and_more'),
        ('TTapp', '0096_breakaroundcoursetype_train_progs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stabilizegroupscourses',
            name='work_copy',
        ),
        migrations.RemoveField(
            model_name='stabilizetutorscourses',
            name='work_copy',
        ),
        migrations.AddField(
            model_name='stabilizegroupscourses',
            name='version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.edtversion'),
        ),
        migrations.AddField(
            model_name='stabilizetutorscourses',
            name='version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.edtversion'),
        ),
    ]