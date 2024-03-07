# Generated by Django 4.2 on 2024-02-28 16:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0118_alter_trainingperiod_department'),
        ('TTapp', '0089_remove_parallelizecourses_course_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='breakaroundcoursetype',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='considertutorsunavailability',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='curfew',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='customconstraint',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='limitcoursetypetimeperperiod',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='limitholes',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='limitsimultaneouscoursesnumber',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='limittutorstimeperperiod',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='limittutortimeperweeks',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='limitundesiredslotsperperiod',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='lowerboundbusydays',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='minimizetutorsbusydays',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='minmoduleshalfdays',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='minnonpreferedtutorsslot',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='mintutorshalfdays',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='modulesbybloc',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='notaloneforthesecousetypes',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='parallelizecourses',
            name='course_types',
        ),
        migrations.RemoveField(
            model_name='parallelizecourses',
            name='modules',
        ),
        migrations.RemoveField(
            model_name='parallelizecourses',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='respecttutorsmaxtimeperday',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='respecttutorsmintimeperday',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='simultaneouscourses',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='stabilizationthroughperiods',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='stabilizetutorscourses',
            name='train_progs',
        ),
        migrations.RemoveField(
            model_name='tutorslunchbreak',
            name='train_progs',
        ),
        migrations.AddField(
            model_name='parallelizecourses',
            name='course_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.coursetype', verbose_name='course type'),
        ),
        migrations.AddField(
            model_name='parallelizecourses',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.module', verbose_name='module'),
        ),
    ]
