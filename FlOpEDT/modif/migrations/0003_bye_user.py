# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-01 21:10
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

def create_fake_user(apps, schema_editor):
    User = get_user_model() #apps.get_model('django.contrib.auth.models', 'User')
    FakeUser = apps.get_model('modif', 'FakeUser')
    Prof = apps.get_model('modif', 'Prof')
    for u in User.objects.all():
        try:
            prof = Prof.objects.get(user__username = u.username)
        except ObjectDoesNotExist:
            print "je croyais que c'était du 1-to-1"
            print u
        fu = FakeUser(
            username = u.username,
            first_name = u.first_name,
            last_name = u.last_name,
            email = u.email,
            password = u.password,
            is_staff = u.is_staff,
            is_active = u.is_active,
            is_superuser = u.is_superuser,
            status = prof.statut,
            pref_slots_per_day = prof.pref_slots_per_day,
            rights = prof.rights,
            LBD = prof.LBD
        )
        fu.save()



def create_tutor_names(apps, schema_editor):

    Module = apps.get_model('modif', 'Module')
    for m in Module.objects.all():
        if m.responsable is not None:
            m.head_name = m.responsable.username
        m.save()

    Disponibilite = apps.get_model('modif', 'Disponibilite')
    for d in Disponibilite.objects.all():
        d.tutor_name = d.prof.user.username
        d.save()

    CoursModification = apps.get_model('modif', 'CoursModification')
    for cm in CoursModification.objects.all():
        cm.initiator_name = cm.user.username
        cm.save()

    PlanifModification = apps.get_model('modif', 'PlanifModification')
    for pm in PlanifModification.objects.all():
        pm.initiator_name = pm.user.username
        if pm.prof_old is not None:
            pm.tutor_name_old = pm.prof_old.username
        pm.save()

    Cours = apps.get_model('modif', 'Cours')
    for c in Cours.objects.all():
        if c.prof is not None:
            c.tutor_name = c.prof.user.username
        if c.profsupp is not None:
            c.supp_tutor_name = c.profsupp.user.username
        c.save()

    CoutProf = apps.get_model('modif', 'CoutProf')
    for cp in CoutProf.objects.all():
        cp.tutor_name = cp.prof.user.username
        cp.save()

    FullStaff = apps.get_model('modif', 'FullStaff')
    FullStaffTmp = apps.get_model('modif', 'FullStaffTmp')
    for fs in FullStaff.objects.all():
        fst = FullStaffTmp(
            tutor_name = fs.user.username,
            department = fs.departement,
            is_iut = fs.is_iut
        )
        fst.save()

    Vacataire = apps.get_model('modif', 'Vacataire')
    VacataireTmp = apps.get_model('modif', 'VacataireTmp')
    for v in Vacataire.objects.all():
        vt = VacataireTmp(
            tutor_name = v.user.username,
            employer = v.employer,
            qualite = v.qualite,
            field = v.field
        )
        vt.save()

    BIATOS = apps.get_model('modif', 'BIATOS')
    BIATOSTmp = apps.get_model('modif', 'BIATOSTmp')
    for b in BIATOS.objects.all():
        bt = BIATOSTmp(
            tutor_name = b.user.username
        )
        bt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('modif', '0002_auto_20180601_2048'),
    ]

    operations = [
        migrations.CreateModel(
            name='BIATOSTmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tutor_name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='FakeUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=100)),
                ('is_staff', models.BooleanField()),
                ('is_active', models.BooleanField()),
                ('is_superuser', models.BooleanField()),
                ('status', models.CharField(choices=[('Vac', 'Vacataire'), ('FuS', 'Permanent UT2J (IUT ou non)'), ('BIA', 'BIATOS')], default='FuS', max_length=3)),
                ('pref_slots_per_day', models.PositiveSmallIntegerField(default=4, verbose_name='Combien de cr\xe9neaux par jour au mieux ?')),
                ('rights', models.PositiveSmallIntegerField(default=0, verbose_name='Peut forcer ?')),
                ('LBD', models.PositiveSmallIntegerField(default=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)], verbose_name='Limitation du nombre de jours')),
            ],
        ),
        migrations.CreateModel(
            name='FullStaffTmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tutor_name', models.CharField(max_length=150)),
                ('department', models.CharField(default='INFO', max_length=50)),
                ('is_iut', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='VacataireTmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tutor_name', models.CharField(max_length=150)),
                ('employer', models.CharField(max_length=50, null=True, verbose_name='Employeur ?')),
                ('qualite', models.CharField(max_length=50, null=True)),
                ('field', models.CharField(max_length=50, null=True, verbose_name='Domaine ?')),
            ],
        ),
        migrations.RemoveField(
            model_name='student',
            name='group',
        ),
        migrations.RemoveField(
            model_name='student',
            name='user',
        ),
        migrations.AddField(
            model_name='cours',
            name='supp_tutor_name',
            field=models.CharField(blank=True, default=None, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='cours',
            name='tutor_name',
            field=models.CharField(default=None, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='coursmodification',
            name='initiator_name',
            field=models.CharField(default=None, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='coutprof',
            name='tutor_name',
            field=models.CharField(default=None, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='disponibilite',
            name='tutor_name',
            field=models.CharField(default=None, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='module',
            name='head_name',
            field=models.CharField(default=None, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='planifmodification',
            name='initiator_name',
            field=models.CharField(default=None, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='planifmodification',
            name='tutor_name_old',
            field=models.CharField(default=None, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='coursmodification',
            name='updated_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='planifmodification',
            name='updated_at',
            field=models.DateTimeField(),
        ),
        migrations.DeleteModel(
            name='Student',
        ),
        migrations.RunPython(create_fake_user),
        migrations.RunPython(create_tutor_names),
    ]
