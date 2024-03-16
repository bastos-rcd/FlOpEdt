# coding:utf-8

# !/usr/bin/python

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.


from TTapp.models import LimitTimePerPeriod, LimitModulesTimePerPeriod, \
    LimitGroupsTimePerPeriod,\
    MinGroupsHalfDays, MinTutorsHalfDays, MinModulesHalfDays,\
    max_weight
from base.models import TrainingProgramme, CourseType, Module, Department, StructuralGroup
from people.models import Tutor
from TTapp.TimetableUtils import add_generic_constraints_to_database

def add_iut_constraints_to_database():
    for department in Department.objects.all():
        add_generic_constraints_to_database(department)
    add_common_constraints()
    add_info_constraints()

def add_common_constraints():
    # Libérer des demi-journées aux étudiants
    for department in Department.objects.filter(abbrev__in=['INFO','RT','GIM','CS']):
        TP = TrainingProgramme.objects.filter(department=department)

        M, created = MinGroupsHalfDays.objects.get_or_create(weight=max_weight, department=department)
        M.save()

        abbrev = department.abbrev
        CM = CourseType.objects.get(name='CM', department=department)
        if abbrev == 'INFO':
            DS = CourseType.objects.get(name='DS', department=department)
        elif abbrev == 'RT':
            DS = CourseType.objects.get(name='Examen', department=department)
        elif abbrev == 'GIM':
            DS = CourseType.objects.get(name='CTRL', department=department)
        else:
            DS = CourseType.objects.get(name='Exam', department=department)

        pas_plus_de_2_exams_par_jour = True
        if pas_plus_de_2_exams_par_jour:
            L, created = LimitGroupsTimePerPeriod.objects.get_or_create(max_hours=3,
                                                                        course_type=DS,
                                                                        period=LimitTimePerPeriod.FULL_DAY,
                                                                        department=department)
            L.save()

        pas_plus_de_2_amphis_par_demi_journee = True

        if pas_plus_de_2_amphis_par_demi_journee:
            L, created = LimitGroupsTimePerPeriod.objects.get_or_create(max_hours=3,
                                                                        course_type=CM,
                                                                        period=LimitTimePerPeriod.HALF_DAY,
                                                                        department=department)
            L.save()

        # Pas plus d'un amphi par matière et par jour
        un_amphi_par_matiere_par_jour = True
        if abbrev in ['RT', 'CS', 'GIM']:
            un_amphi_par_matiere_par_jour = False
        if un_amphi_par_matiere_par_jour:
            L, created = LimitModulesTimePerPeriod.objects.get_or_create(max_hours=2,
                                                                         course_type=CM,
                                                                         period=LimitTimePerPeriod.FULL_DAY,
                                                                         department=department)
            L.save()

        # Pas plus de 1 examens par demi-journée !
        pas_plus_de_1_exam_par_demie_journee = True
        if abbrev in ['INFO', 'CS', 'GIM']:
            pas_plus_de_1_exam_par_demie_journee = False
        if pas_plus_de_1_exam_par_demie_journee:
            L, created = LimitGroupsTimePerPeriod.objects.get_or_create(max_hours=2,
                                                                        course_type=DS,
                                                                        period=LimitTimePerPeriod.HALF_DAY,
                                                                        department=department)
            L.save()

def add_info_constraints():
    department = Department.objects.get(abbrev='INFO')
    lp_apsio = TrainingProgramme.objects.get(abbrev='APSIO')

    M, created = MinModulesHalfDays.objects.get_or_create(weight=max_weight, department=department)
    M.save()
    if created:
        M.train_progs.add(lp_apsio)
        M.save()

    # Impose pour certains vacataires le fait qu'ils viennent sur une seule demi-journée (si moins de 3 cours)
    # C'EST CETTE CONTRAINTE, LORSQU'ELLE N'EST QUE PREFERENCE, QUI CREE LA PAGAILLE DANS CBC!!!

    M, created = MinTutorsHalfDays.objects.get_or_create(join2courses=True, weight=max_weight, department=department)
    M.save()
    if created:
        for i in Tutor.objects.all():
            if i.username in ['AB', 'AJ', 'CDU', 'FMA', 'GRJ', 'JD', 'SD', 'FMO',
                          'JPC', 'MN', 'NJ', 'TC', 'XB', 'PDU', 'VG', 'LC', 'MTH', 'BB']:
                M.tutors.add(i)
        M.save()
