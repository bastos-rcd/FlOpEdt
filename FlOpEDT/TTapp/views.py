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

from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _

from base.models import ScheduledCourse, SchedulingPeriod
from MyFlOp import MyTimetableUtils
from TTapp.admin import GroupsLunchBreakResource
from TTapp.TimetableConstraints.orsay_constraints import GroupsLunchBreak
from TTapp.timetable_utils import get_conflicts


def available_major_versions(_, department, period):
    """
    Send the content of the side panel.
    """
    majors = list(
        ScheduledCourse.objects.filter(
            course__period=period,
            course__type__department__abbrev=department,
        )
        .distinct("version__major")
        .values_list("version__major")
    )
    majors = [n for (n,) in majors]
    majors.sort()
    return JsonResponse({"majors": majors})


def check_swap(_, department, period_id, version):
    """
    Check whether the swap between scheduled courses with work copy
    work_copy and scheduled courses with work copy 0 is feasible
    against the scheduled courses in other departments
    """
    period = SchedulingPeriod.objects.get(id=period_id)
    return JsonResponse(get_conflicts(department, period, version))


def swap(_, department, period_id, major):
    """
    Swap scheduled courses with work copy work_copy
    against scheduled courses with work copy 0
    """
    return JsonResponse(
        MyTimetableUtils.swap_version(department, period_id, major), safe=False
    )


def delete_version(_, department, period_id, major):
    """
    Delete scheduled courses with work copy work_copy
    """
    return JsonResponse(
        MyTimetableUtils.delete_version(department, period_id, major), safe=False
    )


def delete_all_unused_versions(_, department, period_id):
    """
    Delete scheduled courses with work copy work_copy
    """
    return JsonResponse(
        MyTimetableUtils.delete_all_unused_versions(department, period_id),
        safe=False,
    )


def duplicate_version(_, department, period_id, major):
    """
    Duplicate scheduled courses with work copy work_copy in the first work_copy available
    """
    return JsonResponse(
        MyTimetableUtils.duplicate_version(department, period_id, major),
        safe=False,
    )


def reassign_rooms(_, department, period_id, major, create_new_major=True):
    """
    Reassign rooms of scheduled courses with work copy work_copy
    """
    return JsonResponse(
        MyTimetableUtils.reassign_rooms(
            department, period_id, major, create_new_major=create_new_major
        )
    )


def duplicate_in_other_periods(_, department, period_id, major):
    """
    Duplicate all scheduled courses in other weeks
    (for courses that are equals than this week's ones)
    """
    return JsonResponse(
        MyTimetableUtils.duplicate_in_other_periods(department, period_id, major),
        safe=False,
    )


def fetch_group_lunch(req, **kwargs):
    dataset = GroupsLunchBreakResource().export(
        GroupsLunchBreak.objects.filter(department=req.department)
    )
    return HttpResponse(dataset.csv)  # pylint: disable=no-member
