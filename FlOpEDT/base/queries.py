# coding: utf-8
# -*- coding: utf-8 -*-

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

import logging

from django.db import transaction
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

from base.models import StructuralGroup, RoomType, Room, \
    ScheduledCourse, EdtVersion, Department, Regen, \
    Period, TutorCost, CourseStartTimeConstraint, \
    TimeGeneralSettings, GroupType, CourseType, \
    TrainingProgramme, Course, Week

from displayweb.models import GroupDisplay, TrainingProgrammeDisplay, BreakingNews

from people.models import Tutor, NotificationsPreferences, ThemesPreferences
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.FlopConstraint import all_subclasses

logger = logging.getLogger(__name__)


@transaction.atomic
def create_first_department():
    department = Department.objects.create(name="Default Department", abbrev="default")

    T = Tutor.objects.create(username='admin', is_staff=True, is_tutor=True, is_superuser=True, rights=6)
    T.set_password('passe')
    T.save()

    # Update all existing department related models
    models = [
        TrainingProgramme, EdtVersion, Regen, \
        RoomType, Period, CourseType, BreakingNews, \
        TutorCost, GroupType]

    for model in models:
        model.objects.all().update(department=department)

    # Update all ManyToMany relations with Department
    models = [Tutor]
    for model in models:
        for model_class in model.objects.all():
            model_class.departments.add(department)

    # Update existing Constraint
    types = all_subclasses(TTConstraint)

    for type in types:
        type.objects.all().update(department=department)

    return department


def get_edt_version(department, week_nb, year, create=False):
    week = Week.objects.get(nb=week_nb, year=year)

    params = {'week': week, 'department': department}

    if create:
        try:
            edt_version, _ = EdtVersion.objects.get_or_create(defaults={'version': 0}, **params)
        except EdtVersion.MultipleObjectsReturned as e:
            logger.error(f'get_edt_version: database inconsistency, multiple objects returned for {params}')
            raise (e)
        else:
            version = edt_version.version
    else:
        """
        Raise model.DoesNotExist to simulate get behaviour
        when no item is matching filter parameters
        """
        try:
            version = EdtVersion.objects.filter(**params).values_list("version", flat=True)[0]
        except IndexError:
            raise (EdtVersion.DoesNotExist)
    return version


def get_scheduled_courses(department, week, num_copy=0):
    qs = ScheduledCourse.objects \
        .filter(
        course__type__department=department,
        course__week=week,
        day__in=get_working_days(department),
        work_copy=num_copy).select_related('course',
                                           'course__tutor',
                                           'course__module__train_prog',
                                           'course__module',
                                           'course__type',
                                           'room',
                                           'course__room_type',
                                           'course__module__display'
                                           )
    return qs


def get_unscheduled_courses(department, week, year, num_copy):
    return Course.objects.filter(
        module__train_prog__department=department,
        week__nb=week,
        week__year=year
    ).exclude(pk__in=ScheduledCourse.objects.filter(
        course__module__train_prog__department=department,
        work_copy=num_copy
    ).values('course')
              ).select_related('module__train_prog',
                               'tutor',
                               'module',
                               'type',
                               'room_type',
                               'module__display'
                               ).prefetch_related('groups')


def get_groups(department_abbrev):
    """
    Return the groups hierachical representation from database
    """
    final_groups = []

    # Filter TrainingProgramme by department
    training_program_query = TrainingProgramme.objects.filter(department__abbrev=department_abbrev)

    for train_prog in training_program_query:

        gp_dict_children = {}
        gp_master = None
        for gp in StructuralGroup.objects.filter(train_prog=train_prog):
            if gp.full_name in gp_dict_children:
                raise Exception('Group name should be unique')
            if gp.parent_groups.all().count() == 0:
                if gp_master is not None:
                    raise Exception('One single group is able to be without '
                                    'parents')
                gp_master = gp
            elif gp.parent_groups.all().count() > 1:
                raise Exception('Not tree-like group structures are not yet '
                                'handled')
            gp_dict_children[gp.full_name] = []

        if gp_master is None:
            raise Exception(f"Training program {train_prog} does not have any group"
                            f" with no parent.")

        for gp in StructuralGroup.objects.filter(train_prog=train_prog).order_by('name'):
            for new_gp in gp.parent_groups.all():
                gp_dict_children[new_gp.full_name].append(gp)

        final_groups.append(get_descendant_groups(gp_master, gp_dict_children))

    return final_groups


def get_all_connected_courses(group, week, num_copy=0):
    qs = get_scheduled_courses(group.train_prog.department,
                               week, num_copy=num_copy)
    return qs.filter(groups__in=group.connected_groups())


def get_descendant_groups(gp, children):
    """
    Gather informations about all descendants of a group gp
    :param gp:
    :param children: dictionary <group_full_name, list_of_children>
    :return: an object containing the informations on gp and its descendants
    """
    current = {}
    if not gp.parent_groups.all().exists():
        current['parent'] = 'null'
        tp = gp.train_prog
        current['promo'] = tp.abbrev
        try:
            tpd = TrainingProgrammeDisplay.objects.get(training_programme=tp)
            if tpd.short_name != '':
                current['promotxt'] = tpd.short_name
            else:
                current['promotxt'] = tp.abbrev
            current['row'] = tpd.row
        except ObjectDoesNotExist:
            raise Exception('You should indicate on which row a training '
                            'programme will be displayed '
                            '(cf TrainingProgrammeDisplay)')
    current['name'] = gp.name
    try:
        gpd = GroupDisplay.objects.get(group=gp)
        if gpd.button_height is not None:
            current['buth'] = gpd.button_height
        if gpd.button_txt is not None:
            current['buttxt'] = gpd.button_txt
    except ObjectDoesNotExist:
        pass

    if len(children[gp.full_name]) > 0:
        current['children'] = []
        for gp_child in children[gp.full_name]:
            gp_obj = get_descendant_groups(gp_child, children)
            gp_obj['parent'] = gp.name
            current['children'].append(gp_obj)

    return current


def get_room_types_groups(department_abbrev):
    """
    From the data stored in the database, fill the room description file, that
    will be used by the website.
    All room that belongs to a roomgroup that belongs to at least one room type
    of department_abbrev
    :return: an object containing one dictionary roomtype -> (list of roomgroups),
    and one dictionary roomgroup -> (list of rooms)
    """
    dept = Department.objects.get(abbrev=department_abbrev)

    return {'roomtypes': {str(rt): list(set(
        [room.name for room in rt.members.all()]
    )) for rt in RoomType.objects.prefetch_related('members').filter(department=dept)},
        'roomgroups': {room.name: [sub.name for sub in room.and_subrooms()] \
                       for room in
                       Room.objects.prefetch_related('subrooms', 'subrooms__subrooms').filter(departments=dept)}
    }


def get_rooms(department_abbrev, basic=False):
    """
    :return:
    """
    if department_abbrev is not None:
        dept = Department.objects.get(abbrev=department_abbrev)
    else:
        dept = None
    if not basic:
        if dept is None:
            return Room.objects.all()
        else:
            return Room.objects.filter(departments=dept)
    else:
        if dept is None:
            return Room.objects.annotate(nb_sub=Count('subrooms')) \
                .filter(nb_sub=0)
        else:
            return Room.objects.annotate(nb_sub=Count('subrooms')) \
                .filter(departments=dept, nb_sub=0)


def get_coursetype_constraints(department_abbrev):
    """
    From the data stored in the database, fill the course type
    description file (duration and allowed start times), that will
    be used by the website
    :return: a dictionary course type -> (object containing duration
    and list of allowed start times)
    """
    dic = {}
    for ct in CourseType.objects.filter(department__abbrev=department_abbrev):
        dic[ct.name] = {'duration': ct.duration,
                        'allowed_st': []}
        for ct_constraint in \
                CourseStartTimeConstraint.objects.filter(course_type=ct):
            dic[ct.name]['allowed_st'] += ct_constraint.allowed_start_times
        dic[ct.name]['allowed_st'].sort()
        if len(dic[ct.name]['allowed_st']) == 0:
            dic[ct.name]['allowed_st'] += \
                CourseStartTimeConstraint.objects.get(course_type=None).allowed_start_times
    return dic


def get_department_settings(dept):
    """
    :return: time general settings
    """
    ts = dept.timegeneralsettings
    mode = dept.mode
    department_settings = \
        {'time':
             {'day_start_time': ts.day_start_time,
              'day_finish_time': ts.day_finish_time,
              'lunch_break_start_time': ts.lunch_break_start_time,
              'lunch_break_finish_time': ts.lunch_break_finish_time,
              'def_pref_duration': ts.default_preference_duration},
         'days': ts.days,
         'mode':
             {'cosmo': mode.cosmo,
              'visio': str(mode.visio)}
         }
    return department_settings


def get_departments():
    """
    :return: list of department abbreviations
    """
    return [d.abbrev for d in Department.objects.all()]


def get_course_types(dept):
    """
    :return: list of course type names
    """
    return [d.name for d in CourseType.objects.filter(department=dept)]


def get_training_programmes(dept):
    """
    :return: list of training programme names
    """
    return [d.abbrev for d in TrainingProgramme.objects.filter(department=dept)]


def get_working_days(dept):
    """
    :return: list of abbreviated working days in dept
    """
    return TimeGeneralSettings.objects.get(department=dept).days


def get_notification_preference(user):
    if user is not None:
        try:
            return user.notifications_preference.nb_of_notified_weeks
        except NotificationsPreferences.DoesNotExist:
            if user.is_tutor:
                return 4
            elif user.is_student:
                return 0
            else:
                pass
    return 0

###
#
#  Allows to get a user's theme
#  if the user doesn't have a preferred theme yet, it returns "White"
#  @param user : the user
#  @return : the theme
#
###
def get_theme_preference(user):
    if user is not None:
        try:
            return user.get_theme
        except ThemesPreferences.DoesNotExist:
            return 'White'

    return 'White'
