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

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from base.models import ScheduledCourse, Week

from TTapp.TTUtils import get_conflicts

from TTapp.admin import GroupsLunchBreakResource
from TTapp.TTConstraints.orsay_constraints import GroupsLunchBreak

from MyFlOp import MyTTUtils

from django.utils.translation import gettext as _

            
def available_work_copies(req, department, year, week):
    '''
    Send the content of the side panel.
    '''
    copies = list(ScheduledCourse.objects.filter(course__week__year=year, course__week__nb=week,
                                                 course__type__department__abbrev=department).distinct('work_copy')
                  .values_list('work_copy'))
    copies = [n for (n,) in copies]
    copies.sort()
    return JsonResponse({'copies': copies})


def check_swap(req, department, year, week, work_copy):
    '''
    Check whether the swap between scheduled courses with work copy
    work_copy and scheduled courses with work copy 0 is feasible
    against the scheduled courses in other departments
    '''
    print(department, week, year, work_copy)
    week_o = Week.objects.get(nb=week, year=year)
    return JsonResponse(get_conflicts(department, week_o, work_copy))


def swap(req, department, year, week, work_copy):
    '''
    Swap scheduled courses with work copy work_copy
    against scheduled courses with work copy 0
    '''
    return JsonResponse(MyTTUtils.swap_version(department, week, year, work_copy))


def delete_work_copy(req, department, year, week, work_copy):
    '''
    Delete scheduled courses with work copy work_copy
    '''
    return JsonResponse(MyTTUtils.delete_work_copy(department, week, year, work_copy), safe=False)


def delete_all_unused_work_copies(req, department, year, week):
    '''
    Delete scheduled courses with work copy work_copy
    '''
    return JsonResponse(MyTTUtils.delete_all_unused_work_copies(department, week, year), safe=False)


def duplicate_work_copy(req, department, year, week, work_copy):
    '''
    Duplicate scheduled courses with work copy work_copy in the first work_copy available
    '''
    return JsonResponse(MyTTUtils.duplicate_work_copy(department, week, year, work_copy), safe=False)


def reassign_rooms(req, department, year, week, work_copy, create_new_work_copy=True):
    '''
    Reassign rooms of scheduled courses with work copy work_copy
    '''
    return JsonResponse(MyTTUtils.reassign_rooms(department, week, year, work_copy,
                                                 create_new_work_copy=create_new_work_copy))


def duplicate_in_other_weeks(req, department, year, week, work_copy):
    '''
    Duplicate all scheduled courses in other weeks (for courses that are equals than this week's ones)
    '''
    return JsonResponse(MyTTUtils.duplicate_in_other_weeks(department, week, year, work_copy))


def fetch_group_lunch(req, **kwargs):
    dataset = GroupsLunchBreakResource().export(
        GroupsLunchBreak.objects.filter(department=req.department))
    return HttpResponse(dataset.csv)
