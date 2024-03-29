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

import datetime as dt
import logging
import string
from copy import copy
from random import choice

from django.conf import settings as ds
from django.db import IntegrityError, transaction

from base.models import (
    CourseStartTimeConstraint,
    CourseType,
    Department,
    GenericGroup,
    GroupType,
    Mode,
    Module,
    Room,
    RoomType,
    StructuralGroup,
    TimeGeneralSettings,
    TrainingPeriod,
    TrainingProgramme,
    TransversalGroup,
)
from configuration.database_description_checker import database_description_check
from configuration.database_description_xlsx import database_description_load_xlsx_file
from displayweb.models import TrainingProgrammeDisplay
from people.models import (
    FullStaff,
    SupplyStaff,
    Tutor,
    TutorPreference,
    UserDepartmentSettings,
)

logger = logging.getLogger("base")


@transaction.atomic
def extract_database_file(
    department_name=None,
    department_abbrev=None,
    bookname=None,
    book=None,
    fill_default_availabilities=True,
):
    # Test department existence
    department, created = Department.objects.get_or_create(
        name=department_name, abbrev=department_abbrev
    )
    if created:
        try:
            admin = Tutor.objects.get(username="admin")
            UserDepartmentSettings(user=admin, department=department).save()
        except Tutor.DoesNotExist:
            pass

    if not created:
        logger.info(
            "Department with abbrev %s and name %s already exists. "
            "It will be updated",
            department_abbrev,
            department_name,
        )
    if book is None:
        if bookname is None:
            bookname = f"{ds.MEDIA_ROOT}/database_file_{department_abbrev}.xlsx"

        book = database_description_load_xlsx_file(bookname)

    if book is None:
        raise TypeError("Database file could not be loaded.")

    check = database_description_check(book)
    if len(check) > 0:
        raise ValueError("\n".join(check))

    settings_extract(department, book["settings"])
    rooms_extract(
        department, book["room_groups"], book["room_categories"], book["rooms"]
    )
    groups_extract(
        department,
        book["promotions"],
        book["group_types"],
        book["groups"],
        book["transversal_groups"],
    )
    people_extract(department, book["people"], fill_default_availabilities)
    modules_extract(department, book["modules"])
    course_types_extract(department, book["course_types"])
    course_start_time_constraints_extract(
        department, book["course_start_time_constraints"]
    )


def people_extract(department, people, fill_default_availabilities=True):
    logger.info("People extraction : start")
    for id_, person in people.items():
        tutor = Tutor.objects.filter(username=id_)
        if tutor.exists():
            del person["status"]
            del person["employer"]
            tutor.update(**person)
            tutor = tutor.get()
            UserDepartmentSettings.objects.get_or_create(
                department=department, user=tutor
            )
            if fill_default_availabilities:
                pass  # FIX ME : we should split user availabilities in here!
            logger.debug("update tutor : '%s'", id_)

        else:
            try:
                if person["status"] == "Permanent":
                    del person["employer"]
                    tutor = FullStaff(username=id_, **person)
                    tutor.status = Tutor.FULL_STAFF
                else:
                    tutor = SupplyStaff(username=id_, position="Salarié", **person)
                    tutor.status = Tutor.SUPP_STAFF

                tutor.is_tutor = True
                tutor.save()

                UserDepartmentSettings.objects.create(department=department, user=tutor)
                TutorPreference.objects.create(tutor=tutor)

            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected while creating the Professor %s : %s \n",
                    id_,
                    ie,
                )
            else:
                logger.info("create tutor with id: %s", id_)

    logger.info("People extraction : finish")


def rooms_extract(department, room_groups, room_categories, rooms):
    logger.info("Room extraction : start")

    # Create temporary RoomType for import purposes. This type
    # will be deleted at the end of the process
    temporary_room_random_key = "".join(
        choice(string.ascii_lowercase + string.digits) for _ in range(6)
    )
    temporary_room_type = RoomType.objects.create(
        department=department,
        name=f"temp_{department.abbrev}_{temporary_room_random_key}",
    )

    for cat_id in room_categories.keys():
        try:
            RoomType.objects.get_or_create(department=department, name=cat_id)
        except IntegrityError as ie:
            logger.warning(
                "A constraint has not been respected creating the room category '%s' : %s",
                cat_id,
                ie,
            )

    for id_ in rooms:
        try:
            room, _ = Room.objects.get_or_create(name=id_)
            room.types.add(temporary_room_type)
            room.departments.add(department)

        except IntegrityError as ie:
            logger.warning(
                "A constraint has not been respected creating the room '%s' : %s",
                id_,
                ie,
            )

    for group_id, members in room_groups.items():
        try:
            room_group, _ = Room.objects.get_or_create(name=group_id)
            room_group.types.add(temporary_room_type)
            room_group.departments.add(department)

        except IntegrityError as ie:
            logger.warning(
                "A constraint has not been respected creating the room group '%s' : %s",
                group_id,
                ie,
            )

        for room_id in members:
            try:
                room, _ = Room.objects.get_or_create(name=room_id)
                room.departments.add(department)
                if room_group in room.subroom_of.all():
                    continue
                logger.info("Add room '%s' to group '%s'", room_id, group_id)
                room.subroom_of.add(room_group)
                room.departments.add(department)

            except Room.DoesNotExist:
                logger.warning("Unable to find room '%s'", room_id)

    for cat_id, members in room_categories.items():
        room_type = RoomType.objects.get(department=department, name=cat_id)
        for member in members:
            try:
                room = Room.objects.get(name=member)
                room.types.add(room_type)
                room.departments.add(department)
                room.save()
            except Room.DoesNotExist:
                logger.warning("Unable to find room '%s'", member)

    temporary_room_type.delete()
    logger.info("Room extraction : finish")


def groups_extract(department, promotions, group_types, groups, transversal_groups):
    if GenericGroup.objects.exists():
        available_generic_group_id = GenericGroup.objects.latest("id").id + 1
    else:
        available_generic_group_id = 0

    logger.info("Groups extraction : start")
    for id_, name in promotions.items():
        verif = TrainingProgramme.objects.filter(abbrev=id_, department=department)

        if not verif.exists():
            try:
                promotion = TrainingProgramme(
                    department=department, name=name, abbrev=id_
                )
                promotion.save()
                TrainingProgrammeDisplay(training_programme=promotion, row=0).save()
            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected creating the promotion '%s' : %s",
                    id_,
                    ie,
                )

    for id_ in group_types:
        verif = GroupType.objects.filter(name=id_, department=department)

        if not verif.exists():
            try:
                group_type = GroupType(name=id_, department=department)
                group_type.save()

            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected creating the group type '%s' : %s",
                    id_,
                    ie,
                )

    # first loop on groups just to create them - it's too early to set the parents
    for (promotion_id, id_), group in groups.items():
        verif = StructuralGroup.objects.filter(
            name=id_, train_prog__abbrev=promotion_id, train_prog__department=department
        )

        if not verif.exists():
            try:
                promotion = TrainingProgramme.objects.get(
                    abbrev=promotion_id, department=department
                )
                group_type = GroupType.objects.get(
                    name=group["group_type"], department=department
                )
                group = StructuralGroup(
                    name=id_,
                    size=0,
                    train_prog=promotion,
                    type=group_type,
                    id=available_generic_group_id,
                )
                group.save()
                available_generic_group_id += 1

            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected creating the group '%s' : %s",
                    id_,
                    ie,
                )

    # second loop, set the parents

    for (promotion_id, id_), group in groups.items():
        for parent in group["parent"]:
            parent_group = StructuralGroup.objects.get(
                name=parent,
                train_prog__abbrev=promotion_id,
                train_prog__department=department,
            )
            group = StructuralGroup.objects.get(
                name=id_,
                train_prog__abbrev=promotion_id,
                train_prog__department=department,
            )
            group.parent_groups.add(parent_group)
            group.save()

    for g in StructuralGroup.objects.all():
        isbasic = True

        for g1 in StructuralGroup.objects.all():
            if g in g1.parent_groups.all():
                isbasic = False
                break

        g.basic = isbasic
        g.save()

    # first loop on transversal groups just to create them - it's too early to set relatives
    for (promotion_id, id_), transversal_group in transversal_groups.items():
        verif = TransversalGroup.objects.filter(
            name=id_, train_prog__abbrev=promotion_id, train_prog__department=department
        )

        if not verif.exists():
            try:
                promotion = TrainingProgramme.objects.get(
                    abbrev=promotion_id, department=department
                )
                trans_group = TransversalGroup(
                    name=id_,
                    size=0,
                    train_prog=promotion,
                    id=available_generic_group_id,
                )
                trans_group.save()
                available_generic_group_id += 1

            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected creating the transversal group '%s' : %s",
                    id_,
                    ie,
                )

    # second loop, set the relatives

    for (promotion_id, id_), transversal_group in transversal_groups.items():
        t_g = TransversalGroup.objects.get(
            name=id_, train_prog__abbrev=promotion_id, train_prog__department=department
        )

        for group in transversal_group["transversal_to"]:
            conflicting_group = StructuralGroup.objects.get(
                name=group,
                train_prog__abbrev=promotion_id,
                train_prog__department=department,
            )
            t_g.conflicting_groups.add(conflicting_group)
            t_g.save()

        for group in transversal_group["parallel_to"]:
            parallel_group = TransversalGroup.objects.get(
                name=group,
                train_prog__abbrev=promotion_id,
                train_prog__department=department,
            )
            t_g.parallel_groups.add(parallel_group)
            t_g.save()

    logger.info("Groups extraction : finish")


def modules_extract(department, modules):
    logger.info("Modules extraction : start")
    for id_, module in modules.items():
        verif = Module.objects.filter(
            abbrev=id_,
            train_prog__abbrev=module["promotion"],
            train_prog__department=department,
            training_period__name=module["period"],
        )

        if not verif.exists():
            promotion = TrainingProgramme.objects.get(
                abbrev=module["promotion"], department=department
            )
            prof = Tutor.objects.get(username=module["responsable"])
            training_period = TrainingPeriod.objects.get(
                name=module["period"], department=department
            )

            try:
                module = Module(
                    name=module["name"],
                    abbrev=id_,
                    ppn=module["PPN"],
                    train_prog=promotion,
                    head=prof,
                    training_period=training_period,
                )
                module.save()

            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected creating the module '%s' : %s",
                    id_,
                    ie,
                )

    logger.info("Modules extraction : finish")


def course_types_extract(department, course_types):
    logger.info("Courses extraction : start")
    for id_, cours in course_types.items():
        verif = CourseType.objects.filter(name=id_, department=department)

        if not verif.exists():
            try:
                graded = False
                if cours["graded"] == "Oui":
                    graded = True
                course_type = CourseType(name=id_, department=department, graded=graded)
                course_type.save()

                for id_group in cours["group_types"]:
                    group = GroupType.objects.get(name=id_group, department=department)
                    course_type.group_types.add(group)
                    course_type.save()

            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected creating the course type '%s' : %s",
                    id_,
                    ie,
                )
    logger.info("Course types extraction : finish")


def course_start_time_constraints_extract(department, course_start_time_constraints):
    logger.info("Course start time constraints extraction : start")
    for duration_str, cstc in course_start_time_constraints.items():
        duration = dt.timedelta(minutes=int(duration_str))

        verif = CourseStartTimeConstraint.objects.filter(
            duration=duration, department=department
        )

        if not verif.exists():
            try:
                time_constraint = CourseStartTimeConstraint(
                    allowed_start_times=list(cstc["start_times"]),
                    department=department,
                    duration=duration,
                )
                time_constraint.save()

            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected creating the duration constraint %s : %s",
                    duration_str,
                    ie,
                )
    logger.info("Courses extraction : finish")


def convert_time(value):
    """
    Return an integer value from a time (hh:mm:ss) formated value
    representing the number of minutes since midnight
    """
    time_array = value.split(":")
    return int(time_array[0]) * 60 + int(time_array[1])


def settings_extract(department: Department, settings):
    logger.info("Settings extraction : start")
    modes = settings["mode"]
    verif = Mode.objects.filter(department=department)
    if verif.exists():
        mode = verif[0]
        mode.cosmo = modes["cosmo"]
        mode.visio = modes["visio"]
        mode.scheduling_mode = modes["scheduling_mode"]
        mode.save()
        logger.info("Mode has been updated")
    else:
        mode = Mode.objects.create(
            department=department,
            cosmo=modes["cosmo"],
            visio=modes["visio"],
            scheduling_mode=modes["scheduling_mode"],
        )
        logger.info("Mode has been created")

    for id_, (start_date, end_date) in settings["training_periods"].items():
        considered_scheduling_periods = department.scheduling_periods().filter(
            end_date__gte=start_date, start_date__lte=end_date
        )

        verif = TrainingPeriod.objects.filter(department=department, name=id_)

        if verif.exists():
            training_period = verif[0]
            if set(training_period.periods.all()) != set(considered_scheduling_periods):
                training_period.periods.set(considered_scheduling_periods)
                logger.info(
                    " Training_period %s' scheduling periods have been updated", id_
                )
        else:
            try:
                training_period = TrainingPeriod.objects.create(
                    name=id_, department=department
                )
                training_period.periods.set(considered_scheduling_periods)

            except IntegrityError as ie:
                logger.warning(
                    "A constraint has not been respected creating the period ''%s' : %s",
                    id_,
                    ie,
                )

    params = copy(settings)
    del params["training_periods"]
    del params["mode"]
    logger.info("TimeGeneralSettings : %s", params)
    TimeGeneralSettings.objects.filter(department=department).delete()
    TimeGeneralSettings.objects.create(department=department, **params)
    logger.info("Settings extraction : finish")
