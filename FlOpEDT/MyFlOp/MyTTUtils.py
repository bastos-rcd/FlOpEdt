# coding:utf-8

# !/usr/bin/python3

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
import functools

from TTapp.TTUtils import basic_reassign_rooms, basic_swap_version, \
    basic_delete_work_copy, basic_duplicate_work_copy, basic_delete_all_unused_work_copies, \
    duplicate_what_can_be_in_other_periods, number_courses
from base.models import ScheduledCourse, Department, SchedulingPeriod
from people.models import Tutor


def resolve_department(func):

    # Replace department attribute by the target
    # department instance if needed

    @functools.wraps(func)
    def _wraper_function(department, *args, **kwargs):

        if type(department) is str:
            department = Department.objects.get(abbrev=department)

        return func(department, *args, **kwargs)

    return _wraper_function

def print_differences(department, periods, old_copy, new_copy, tutors=Tutor.objects.all()):
    for period in periods:
        print("For", period)
        for tutor in tutors:
            SCa = ScheduledCourse.objects.filter(course__tutor=tutor, work_copy=old_copy, course__period=period,
                                                 course__type__department=department)
            SCb = ScheduledCourse.objects.filter(course__tutor=tutor, work_copy=new_copy, course__period=period,
                                                 course__type__department=department)
            slots_a = set([(x.day, x.start_time//60) for x in SCa])
            slots_b = set([(x.day, x.start_time//60) for x in SCb])
            if slots_a ^ slots_b:
                result = "For %s old copy has :" % tutor
                for sl in slots_a - slots_b:
                    result += "%s, " % str(sl)
                result += "and new copy has :"
                for sl in slots_b - slots_a:
                    result += "%s, " % str(sl)
                print(result)


@resolve_department
def reassign_rooms(department, period_id, work_copy, create_new_work_copy=True):
    period = SchedulingPeriod.objects.get(id=period_id)
    result = basic_reassign_rooms(department, period, work_copy, create_new_work_copy=create_new_work_copy)
    return result


@resolve_department
def swap_version(department, period_id, copy_a, copy_b=0):
    result = {'status':'OK', 'more':''}
    period = SchedulingPeriod.objects.get(id=period_id)
    basic_swap_version(department, period, copy_a, copy_b)
    return result


@resolve_department
def delete_work_copy(department, period_id, work_copy):
    period = SchedulingPeriod.objects.get(id=period_id)
    return basic_delete_work_copy(department, period, work_copy)


@resolve_department
def delete_all_unused_work_copies(department, period_id):
    period = SchedulingPeriod.objects.get(id=period_id)
    return basic_delete_all_unused_work_copies(department, period)


@resolve_department
def duplicate_work_copy(department, period_id, work_copy):
    period = SchedulingPeriod.objects.get(id=period_id)
    return basic_duplicate_work_copy(department, period, work_copy)


@resolve_department
def duplicate_in_other_periods(department, period_id, work_copy):
    period = SchedulingPeriod.objects.get(id=period_id)
    return duplicate_what_can_be_in_other_periods(department, period, work_copy)


@resolve_department
def number_courses_from_this_period(department, period_id, work_copy):
    if work_copy != 0:
        return
    period = SchedulingPeriod.objects.get(id=period_id)
    return number_courses(department, from_period=period)
