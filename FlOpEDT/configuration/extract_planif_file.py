# coding: utf-8
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

import os
import sys
from openpyxl import *

from base.models import (
    GenericGroup,
    Module,
    Course,
    CourseType,
    RoomType,
    TrainingProgramme,
    Dependency,
    TrainingPeriod,
    Department,
    CoursePossibleTutors,
    ModuleTutorRepartition,
    CourseAdditional,
    SchedulingPeriod,
)
from people.models import Tutor, UserDepartmentSettings
from misc.assign_colors import assign_module_color
from TTapp.models import StabilizationThroughPeriods

from django.db import transaction
from django.db.models import Q
from django.conf import settings as ds

import datetime as dt

def do_assign(module, course_type, period, book):
    already_done = ModuleTutorRepartition.objects.filter(
        module=module, course_type=course_type, period=period
    ).exists()
    if already_done:
        return

    assignation_sheet = book["ModuleTutorsAssignation"]
    assign_ok = False
    for assignation_row in range(1, 100):
        if (
            assignation_sheet.cell(row=assignation_row, column=1).value == module.abbrev
            and assignation_sheet.cell(row=assignation_row, column=2).value
            == course_type.name
        ):
            assign_ok = True
            break
    if not assign_ok:
        raise Exception(
            f"Rien n'est prévu pour assigner {module.abbrev} / {course_type.name}..."
        )
    column = 3
    tutor_username = assignation_sheet.cell(row=assignation_row, column=column).value
    while tutor_username is not None:
        tutor = Tutor.objects.get(username=tutor_username)
        mtr = ModuleTutorRepartition(
            module=module, course_type=course_type, period=period, tutor=tutor
        )
        nb = assignation_sheet.cell(row=assignation_row + 1, column=column).value
        if nb is not None:
            nb = int(nb)
            mtr.courses_nb = nb
        mtr.save()
        column += 1
        tutor_username = assignation_sheet.cell(
            row=assignation_row, column=column
        ).value
    print(f"Assignation done for {module.abbrev} / {course_type.name}!")


@transaction.atomic
def ReadPlanifSchedulingPeriod(department, book, feuille, period: SchedulingPeriod, courses_to_stabilize=None):
    sheet = book[feuille]
    training_period = TrainingPeriod.objects.get(name=feuille, department=department)
    Course.objects.filter(
        type__department=department, period=period, module__training_period=training_period
    ).delete()
    after_type_dependencies = []
    # lookup period column

    wc = 7
    for wr in [1]:
        while wc < 100:
            wc += 1
            short_period_name = sheet.cell(row=wr, column=wc).value
            if short_period_name is None or short_period_name == "VERIF":
                print("Pas de période %s en %s" % (period.name, feuille))
                return
            if period.name.startswith(short_period_name) :
                PERIOD_COL = wc
                break
    print("Période %s de %s : colonne %g" % (period.name, feuille, PERIOD_COL))

    row = 4
    module_COL = 1
    nature_COL = 3
    duration_COL = 4
    prof_COL = 5
    room_type_COL = 6
    group_COL = 7
    sumtotal = 0
    while 1:
        row += 1
        if courses_to_stabilize is not None:
            if row not in courses_to_stabilize:
                courses_to_stabilize[row] = []
        is_total = sheet.cell(row=row, column=group_COL).value
        if is_total == "TOTAL":
            # print "Period %g de %s - TOTAL: %g"%(period, feuille,sumtotal)
            break

        Cell = sheet.cell(row=row, column=PERIOD_COL)
        N = Cell.value
        if N is None:
            continue

        try:
            room_type = sheet.cell(row=row, column=room_type_COL).value
            module = sheet.cell(row=row, column=module_COL).value
            N = float(N)
            # handle dark green lines - Vert fonce
            assert isinstance(room_type, str) and room_type is not None
            if room_type == "Type de Salle":
                nominal = int(N)
                if N != nominal:
                    print(
                        "Valeur decimale ligne %g de %s, période %g : on la met a 1 !"
                        % (row, feuille, period.name)
                    )
                    nominal = 1
                    # le nominal est le nombre de cours par groupe (de TP ou TD)
                if Cell.comment:
                    comments = (
                        Cell.comment.text.replace(" ", "")
                        .replace("\n", "")
                        .replace(",", ";")
                        .split(";")
                    )
                else:
                    comments = []

                sumtotal += nominal

                continue
            try:
                comments = comments
            except:
                comments = []

            # handle light green lines - Vert clair
            MODULE = Module.objects.get(abbrev=module, training_period=training_period)
            PROMO = MODULE.train_prog
            nature = sheet.cell(row=row, column=nature_COL).value
            prof = sheet.cell(row=row, column=prof_COL).value
            grps = sheet.cell(row=row, column=group_COL).value
            COURSE_TYPE = CourseType.objects.get(name=nature, department=department)
            ROOM_TYPE = RoomType.objects.get(name=room_type, department=department)
            DURATION = dt.timedelta(minutes = sheet.cell(row=row, column=duration_COL).value)
            supp_profs = []
            possible_profs = []
            if prof is None:
                TUTOR = None
            elif prof == "*":
                TUTOR = None
                do_assign(MODULE, COURSE_TYPE, period, book)
            else:
                assert isinstance(prof, str)
                prof = prof.replace("\xa0", "").replace(" ", "")
                if "|" in prof:
                    possible_profs = prof.split("|")
                    TUTOR = None
                else:
                    profs = prof.split(";")
                    prof = profs[0]
                    TUTOR = Tutor.objects.get(username=prof)
                    supp_profs = profs[1:]

            if Cell.comment:
                local_comments = (
                    Cell.comment.text.replace("\xa0", "")
                    .replace(" ", "")
                    .replace("\n", "")
                    .replace(",", ";")
                    .split(";")
                )
            else:
                local_comments = []

            all_comments = comments + local_comments

            if isinstance(grps, int) or isinstance(grps, float):
                grps = str(int(grps))
            if not grps:
                grps = []
            else:
                grps = (
                    grps.replace("\xa0", "")
                    .replace(" ", "")
                    .replace(",", ";")
                    .split(";")
                )
            groups = [str(g) for g in grps]

            GROUPS = list(
                GenericGroup.objects.filter(name__in=groups, train_prog=PROMO)
            )
            if not GROUPS:
                raise Exception(
                    f"Group(s) do(es) not exist {row}, period {period.name} of {feuille}\n"
                )

            N = int(N)

            for i in range(N):
                C = Course(
                    tutor=TUTOR,
                    type=COURSE_TYPE,
                    module=MODULE,
                    period=period,
                    room_type=ROOM_TYPE,
                    duration=DURATION,
                )
                C.save()
                if courses_to_stabilize is not None:
                    courses_to_stabilize[row].append(C)
                for g in GROUPS:
                    C.groups.add(g)
                C.save()
                if supp_profs != []:
                    SUPP_TUTORS = Tutor.objects.filter(username__in=supp_profs)
                    for sp in SUPP_TUTORS:
                        C.supp_tutor.add(sp)
                    C.save()
                if possible_profs != []:
                    cpt = CoursePossibleTutors(course=C)
                    cpt.save()
                    for pp in possible_profs:
                        t = Tutor.objects.get(username=pp)
                        cpt.possible_tutors.add(t)
                    cpt.save()

                for after_type in [x for x in all_comments if x[0] == "A"]:
                    try:
                        n = int(after_type[1])
                        s = 2
                    except ValueError:
                        n = 1
                        s = 1
                    course_type = after_type[s:]
                    relevant_groups = set()
                    for g in GROUPS:
                        relevant_groups |= (
                            g.ancestor_groups() | {g} | g.descendants_groups()
                        )
                    course_type_queryset = Course.objects.filter(
                        type__name=course_type,
                        module=MODULE,
                        period=period,
                        groups__in=relevant_groups,
                    ).exclude(id=C.id)
                    for relevant_group in relevant_groups:
                        courses_queryset = course_type_queryset.filter(groups=relevant_group)
                        if courses_queryset.exists():
                            after_type_dependencies.append((C.id, courses_queryset, n, row))

                if "P" in all_comments:
                    course_additional, created = CourseAdditional.objects.get_or_create(
                        course=C
                    )
                    course_additional.visio_preference_value = 0
                    course_additional.save()
                elif "DI" in all_comments:
                    course_additional, created = CourseAdditional.objects.get_or_create(
                        course=C
                    )
                    course_additional.visio_preference_value = 8
                    course_additional.save()
                if "E" in all_comments:
                    course_additional, created = CourseAdditional.objects.get_or_create(
                        course=C
                    )
                    course_additional.graded = True
                    course_additional.save()
            if "D" in comments or "D" in local_comments and N >= 2:
                relevant_courses = Course.objects.filter(
                    type=COURSE_TYPE, module=MODULE, groups__in=GROUPS, period=period
                )
                for i in range(N // 2):
                    P = Dependency(
                        course1=relevant_courses[2 * i],
                        course2=relevant_courses[2 * i + 1],
                        successive=True,
                    )
                    P.save()
            if "ND" in comments or "ND" in local_comments and N >= 2:
                relevant_courses = Course.objects.filter(
                    type=COURSE_TYPE, module=MODULE, groups__in=GROUPS, period=period
                )
                for i in range(N - 1):
                    P = Dependency(
                        course1=relevant_courses[i],
                        course2=relevant_courses[i + 1],
                        day_gap=1,
                    )
                    P.save()

        except Exception as e:
            raise Exception(
                f"Exception ligne {row}, période {period.name} de {feuille}: {e} \n"
            )

    # Add after_type dependecies
    for id, courses_queryset, n, row in after_type_dependencies:
        course2 = Course.objects.get(id=id)
        for course1 in courses_queryset[:n]:
            P = Dependency.objects.create(course1=course1, course2=course2)        


@transaction.atomic
def extract_training_period(
    department,
    book,
    training_period: TrainingPeriod,
    stabilize_courses=False,
    periods = []
):

    if stabilize_courses:
        courses_to_stabilize = {}
        print("Courses will be stabilized through scheduling periods for training period", training_period)
    else:
        courses_to_stabilize = None
    considered_periods = set(training_period.periods.all())
    if periods is not None:
        considered_periods &= set(periods)
    considered_periods = list(considered_periods)
    considered_periods.sort()
    for period in considered_periods:
        ReadPlanifSchedulingPeriod(department, book, training_period.name, period, courses_to_stabilize)

    if stabilize_courses:
        for courses_list in courses_to_stabilize.values():
            if len(courses_list) < 2:
                continue
            stw = StabilizationThroughPeriods.objects.create(department=department)
            for c in courses_list:
                stw.courses.add(c)


@transaction.atomic
def extract_planif(
    department,
    bookname=None,
    stabilize_courses=False,
    scheduling_periods=None,
    training_periods=None,
    assign_colors=True,
):
    """
    Generate the courses from bookname; the school year starts in actual_year
    """
    if bookname is None:
        bookname = os.path.join(ds.MEDIA_ROOT,'media/configuration/planif_file_'+department.abbrev+'.xlsx')
    book = load_workbook(filename=bookname, data_only=True)
    training_periods = define_training_periods(department, book, training_periods)
    for training_period in training_periods:
        extract_training_period(
            department,
            book,
            training_period,
            stabilize_courses,
            periods=scheduling_periods,
        )
    if assign_colors:
        assign_module_color(department, overwrite=True)


@transaction.atomic
def extract_planif_scheduling_periods(scheduling_periods, department, bookname=None, training_periods=None):
    if bookname is None:
        bookname = os.path.join(ds.MEDIA_ROOT,'media/configuration/planif_file_'+department.abbrev+'.xlsx')
    book = load_workbook(filename=bookname, data_only=True)
    training_periods = define_training_periods(department, book, training_periods)
    for training_period in training_periods:
        for scheduling_period in scheduling_periods:
            ReadPlanifSchedulingPeriod(department, book, training_period.name, scheduling_period)


def define_training_periods(department, book, training_periods):
    if training_periods is None:
        training_periods = TrainingPeriod.objects.filter(department=department)
    ok_training_periods = []
    for training_period in training_periods:
        if training_period.name in book:
            ok_training_periods.append(training_period)
    return ok_training_periods
