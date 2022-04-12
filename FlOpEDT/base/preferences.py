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

from base.models import CourseStartTimeConstraint, Course, UserPreference, Week
from TTapp.FlopConstraint import max_weight


def split_preferences(tutor, departments=None):
    splits = set()
    days = set()
    if departments is None:
        departments = tutor.departments.all()


    # compute all possible times of events in the departments
    for dpt in departments:
        courses = \
            Course.objects.select_related('module__train_prog__department')\
                          .filter(module__train_prog__department=dpt)\
                          .distinct('type')
        for course_type in [c.type for c in courses]:
            for time_constraints in \
                CourseStartTimeConstraint.objects\
                                         .filter(course_type=course_type):
                splits |= set(time_constraints.allowed_start_times)
                splits |= \
                    set([start + course_type.duration
                         for start in time_constraints.allowed_start_times])

        days |= set(dpt.timegeneralsettings.days)

    min_day = min([d.timegeneralsettings.day_start_time for d in departments])
    max_day = max([d.timegeneralsettings.day_finish_time for d in departments])
    max_am = max([d.timegeneralsettings.lunch_break_start_time for d in departments])
    min_pm = min([d.timegeneralsettings.lunch_break_finish_time for d in departments])

    if min_pm <= max_am:
        split_apm = list(splits | set([min_day, max_day]))
        split_apm.sort()
        intervals = [split_apm]
    else:
        am = list(filter(lambda s: s > min_day and s < max_am, splits))
        am.sort()
        split_am = [min_day] + am + [max_am]
        pm = list(filter(lambda s: s > min_pm and s < max_day, splits))
        pm.sort()
        split_pm = [min_pm] + pm + [max_day]
        intervals = [split_am, split_pm]

    considered_user_pref = UserPreference\
        .objects\
        .filter(user=tutor)\
        .distinct('week')

    weeks = [user_pref.week for user_pref in considered_user_pref]

    # create typical week if non existing
    if None not in weeks:
        # if database has been flushed, create all necessary weeks
        if not Week.objects.exists():
            for y in range(10, 51):
                year = 2000 + y
                if y in {20, 26, 32, 37, 48}:
                    final_week = 53
                else:
                    final_week = 52
                for w_nb in range(1, final_week + 1):
                    Week.objects.get_or_create(nb=w_nb, year=year)
        # QuerySet does not support append
        weeks.append(None)
    
    for week in weeks:
        for d in days:

            # store old preferences in a more friendly way
            # and delete them from the database
            pref_time = []
            pref_val = []
            pref_slots = UserPreference.objects\
                                       .filter(user=tutor, day=d, week=week)\
                                       .order_by('start_time')

            for slot in pref_slots:
                if len(pref_time) == 0:
                    pref_time.append(slot.start_time)
                    pref_time.append(slot.start_time + slot.duration)
                    pref_val.append(slot.value)
                else:
                    # overlapping preference interval
                    if slot.start_time < pref_time[-1]:
                        if slot.start_time + slot.duration  > pref_time[-1]:
                            slot.duration -= pref_time[-1] - slot.start_time
                            slot.start_time = pref_time[-1]
                    
                    mid = int((pref_time[-1] + slot.start_time)/2)
                    pref_time[-1] = mid
                    pref_time.append(slot.start_time + slot.duration)
                    pref_val.append(slot.value)

            pref_slots.delete()

            # translate preferences into new splits
            # and store them in the DB
            j_before = 0
            for inter in intervals:
                
                # preferences might be empty
                if len(pref_time) == 0:
                    pref_time.append(inter[0])
                    pref_time.append(inter[-1])
                    pref_val.append(max_weight)

                for i in range(len(inter) - 1):
                    while j_before + 1 < len(pref_time) \
                          and pref_time[j_before+1] <= inter[i]:
                        j_before += 1
                        
                    if j_before + 1 == len(pref_time):
                        # out of bounds
                        val = max_weight
                    else:
                        val = pref_val[j_before]
                    
                    j_after = j_before
                    
                    while j_after + 1 < len(pref_time) \
                          and pref_time[j_after+1] < inter[i+1]:
                        val = min(val, pref_val[j_after])
                        j_after += 1
                        
                    j_before = j_after

                    UserPreference.objects.create(
                        user=tutor,
                        day=d,
                        start_time=inter[i],
                        duration=inter[i+1]-inter[i],
                        value=val,
                        week=week
                    )
