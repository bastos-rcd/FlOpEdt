#!/usr/bin/env python3
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
from django.core.mail import EmailMessage
from pulp import LpVariable, LpConstraint, LpBinary, LpConstraintEQ, \
    LpConstraintGE, LpConstraintLE, LpAffineExpression, LpProblem, LpStatus, \
    LpMinimize, lpSum, LpStatusOptimal, LpStatusNotSolved

import pulp
from pulp import GUROBI_CMD

from django.conf import settings

from base.models import Group, \
    Room, RoomSort, RoomType, RoomPreference, \
    Course, ScheduledCourse, UserPreference, CoursePreference, \
    Department, Module, TrainingProgramme, CourseType, \
    Dependency, TutorCost, GroupFreeHalfDay, GroupCost, Holiday, TrainingHalfDay, \
    CourseStartTimeConstraint, TimeGeneralSettings, ModulePossibleTutors, CoursePossibleTutors, CourseAdditional

from base.timing import Time, Day

import base.queries as queries

from people.models import Tutor, PhysicalPresence


from TTapp.slots import Slot, CourseSlot, slots_filter, days_filter

from django.db.models import Q, Max, F

import logging

from base.models import ModuleTutorRepartition


logger = logging.getLogger(__name__)
pattern = r".+: (.|\s)+ (=|>=|<=) \d*"
GUROBI = 'GUROBI'
GUROBI_NAME = 'GUROBI_CMD'


class WeeksDatabase(object):
    def __init__(self, department, weeks, train_prog, slots_step=None):
        self.train_prog = train_prog
        self.department = department
        self.weeks = weeks
        self.slots_step = slots_step
        self.possible_apms=set()
        self.days, self.day_after, self.holidays, self.training_half_days, self.day_before = self.days_init()
        self.course_types, self.courses, self.courses_by_week, \
            self.sched_courses, self.fixed_courses, \
            self.other_departments_courses, self.other_departments_sched_courses, \
            self.courses_availabilities, self.modules, self.dependencies = self.courses_init()
        self.courses_slots, self.availability_slots, \
            self.first_hour_slots, self.last_hour_slots = self.slots_init()
        self.fixed_courses_for_avail_slot, self.other_departments_sched_courses_for_avail_slot = \
            self.courses_for_avail_slot_init()
        if self.department.mode.visio:
            self.visio_courses, self.no_visio_courses, self.visio_ponderation = self.visio_init()
        self.room_types, self.rooms, self.basic_rooms, self.room_prefs, self.rooms_for_type, \
            self.room_course_compat, self.course_rg_compat, self.fixed_courses_for_room, \
            self.other_departments_sched_courses_for_room = self.rooms_init()
        self.compatible_slots, self.compatible_courses = self.compatibilities_init()
        self.groups, self.basic_groups, self.all_groups_of, self.basic_groups_of, self.courses_for_group, \
            self.courses_for_basic_group = self.groups_init()
        self.instructors, self.courses_for_tutor, self.courses_for_supp_tutor, self.availabilities, \
            self.fixed_courses_for_tutor, \
            self.other_departments_courses_for_tutor, self.other_departments_scheduled_courses_for_supp_tutor, \
            self.other_departments_scheduled_courses_for_tutor, \
            self.physical_presence_days_for_tutor = self.users_init()
        self.possible_tutors, self.possible_modules, self.possible_courses = self.possible_courses_tutor_init()

    def days_init(self):

        training_half_days = TrainingHalfDay.objects.filter(
            week__in=self.weeks,
            train_prog__in=self.train_prog)

        days = [Day(week=week, day=day)
                for week in self.weeks
                for day in TimeGeneralSettings.objects.get(department=self.department).days]

        database_holidays = Holiday.objects.filter(week__in=self.weeks)
        holidays = set(d for d in days if database_holidays.filter(day=d.day, week=d.week).exists())

        if self.department.mode.cosmo != 1:
            for hd in holidays:
                days.remove(hd)

        day_after = {}
        for i, day in enumerate(days):
            try:
                day_after[day] = days[i + 1]
            except IndexError:
                day_after[day] = None

        day_before = {}
        for i, day in enumerate(days):
            if i == 0:
                day_before[day] = None
            else:
                day_before[day] = days[i-1]

        days = set(days)

        return days, day_after, holidays, training_half_days, day_before

    def slots_init(self):
        # SLOTS
        print('Slot tools definition', end=', ')
        tgs = TimeGeneralSettings.objects.get(department=self.department)
        courses_slots = set()
        filtered_cstc = CourseStartTimeConstraint.objects.filter(Q(course_type__in=self.course_types)
                                                                 | Q(course_type=None))
        # Courses slots
        for cc in filtered_cstc:
            start_times = cc.allowed_start_times
            if self.slots_step is None:
                courses_slots |= set(CourseSlot(d, start_time, cc.course_type)
                             for d in self.days
                             for start_time in start_times)
            else:
                courses_slots |= set(CourseSlot(d, start_time, cc.course_type)
                                     for d in self.days
                                     for start_time in cc.allowed_start_times if start_time % self.slots_step == 0)

        for slot in courses_slots:
            self.possible_apms.add(slot.apm)

        # We build availability slots considering the possible Intervals from a possible start time to another
        # and adding the possible end times. It is a partition, and we may use the Partition class to do it.
        dayly_availability_slots= set()
        for cst in filtered_cstc:
            dayly_availability_slots |= set(cst.allowed_start_times)
            if cst.course_type is not None:
                dayly_availability_slots |= set(st + cst.course_type.duration for st in cst.allowed_start_times)
        dayly_availability_slots.add(tgs.day_finish_time)
        dayly_availability_slots = list(dayly_availability_slots)
        dayly_availability_slots.sort()
        start_times = dayly_availability_slots[:-1]
        end_times = dayly_availability_slots[1:]
        if tgs.lunch_break_start_time < tgs.lunch_break_finish_time and \
                tgs.lunch_break_start_time in start_times and \
                tgs.lunch_break_finish_time in end_times:
            start_times.remove(tgs.lunch_break_start_time)
            end_times.remove(tgs.lunch_break_finish_time)

        availability_slots = {Slot(day=day,
                                   start_time=start_times[i],
                                   end_time=end_times[i])
                              for day in self.days
                              for i in range(len(start_times))}
        print('Ok' + f' : {len(courses_slots)} courses_slots and {len(availability_slots)} availability_slots created!')

        first_hour_slots = {slot for slot in availability_slots if slot.start_time < start_times[0] + 60}

        last_hour_slots = {slot for slot in availability_slots if slot.end_time > end_times[-1] - 60}

        return courses_slots, availability_slots, first_hour_slots, last_hour_slots

    def courses_init(self):
        # COURSES
        courses = Course.objects.filter(week__in=self.weeks, module__train_prog__in=self.train_prog)\
            .select_related('module')

        course_types = set(c.type for c in courses)

        courses_by_week = {week: set(courses.filter(week=week)) for week in self.weeks}

        sched_courses = ScheduledCourse \
            .objects \
            .filter(course__week__in=self.weeks,
                    course__module__train_prog__in=self.train_prog,
                    work_copy=0)

        fixed_courses = ScheduledCourse.objects \
            .filter(course__module__train_prog__department=self.department,
                    course__week__in=self.weeks,
                    work_copy=0) \
            .exclude(course__module__train_prog__in=self.train_prog)

        other_departments_courses = Course.objects.filter(
            week__in=self.weeks) \
            .exclude(type__department=self.department)

        other_departments_sched_courses = ScheduledCourse \
            .objects \
            .filter(course__in=other_departments_courses,
                    work_copy=0)

        courses_availabilities = CoursePreference.objects \
            .filter(Q(week__in=self.weeks) | Q(week=None),
                    train_prog__department=self.department)

        modules = Module.objects \
            .filter(id__in=courses.values_list('module_id').distinct())

        dependencies = Dependency.objects.filter(
            course1__week__in=self.weeks,
            course2__week__in=self.weeks,
            course1__module__train_prog__in=self.train_prog)

        return course_types, courses, courses_by_week, sched_courses, fixed_courses, \
               other_departments_courses, other_departments_sched_courses, \
               courses_availabilities, modules, dependencies

    def courses_for_avail_slot_init(self):
        fixed_courses_for_avail_slot = {}
        for sl in self.availability_slots:
            fixed_courses_for_avail_slot[sl] = set(fc for fc in self.fixed_courses
                                                   if sl.is_simultaneous_to(fc))

        other_departments_sched_courses_for_avail_slot = {}
        for sl in self.availability_slots:
            other_departments_sched_courses_for_avail_slot[sl] = \
                set(fc for fc in self.other_departments_sched_courses
                    if fc.start_time < sl.end_time and sl.start_time < fc.end_time
                    and fc.day == sl.day.day and fc.course.week == sl.day.week)

        return fixed_courses_for_avail_slot, other_departments_sched_courses_for_avail_slot

    def rooms_init(self):
        # ROOMS
        room_types = RoomType.objects.filter(department=self.department)
        basic_rooms = queries.get_rooms(self.department.abbrev, basic=True).distinct()
        room_prefs = RoomSort.objects.filter(for_type__department=self.department)
        rooms_for_type = {t: t.members.all() for t in room_types}

        rooms = set(Room.objects.filter(departments=self.department).distinct())
        for r in basic_rooms:
            rooms |= r.and_overrooms()

        course_rg_compat = {}
        for c in self.courses:
            course_rg_compat[c] = set(c.room_type.members.all())

        # for each Room, build the list of courses that may use it
        room_course_compat = {}
        for r in basic_rooms:
            # print "compat for ", r
            room_course_compat[r] = []
            for rg in r.and_overrooms():
                room_course_compat[r].extend(
                    [(c, rg) for c in self.courses if rg in course_rg_compat[c]])
                     # self.courses.filter(room_type__in=rg.types.all())])
        if self.department.mode.visio:
            # All courses can have no room (except no-visio ones?)
            for c in set(self.courses):
                # if c not in self.no_visio_courses:
                course_rg_compat[c].add(None)
        fixed_courses_for_room = {}
        for r in basic_rooms:
            fixed_courses_for_room[r] = set()
            for rg in r.and_overrooms():
                fixed_courses_for_room[r] |= set(self.fixed_courses.filter(room=rg))

        other_departments_sched_courses_for_room = {}
        for r in basic_rooms:
            other_departments_sched_courses_for_room[r] = set()
            for rg in r.and_overrooms():
                other_departments_sched_courses_for_room[r] |= set(self.other_departments_sched_courses.filter(room=rg))

        return room_types, rooms, basic_rooms, room_prefs, rooms_for_type, room_course_compat, course_rg_compat, \
               fixed_courses_for_room, other_departments_sched_courses_for_room

    def compatibilities_init(self):
        # COMPATIBILITY
        # Slots and courses are compatible if they have the same type
        # OR if slot type is None and they have the same duration
        if not self.department.mode.cosmo:
            compatible_slots = {}
            for c in self.courses:
                compatible_slots[c] = set(slot for slot in self.courses_slots
                                          if slot.day.week == c.week and
                                          (slot.course_type == c.type
                                           or (slot.course_type is None and c.type.duration == slot.duration)))

            compatible_courses = {}
            for sl in self.courses_slots:
                if sl.course_type is None:
                    compatible_courses[sl] = set(course for course in self.courses
                                                 if course.type.duration == sl.duration
                                                 and sl.day.week == course.week)
                else:
                    compatible_courses[sl] = set(course for course in self.courses
                                                 if course.type == sl.course_type
                                                 and sl.day.week == course.week)
        else:
            compatible_courses = {sl: set() for sl in self.courses_slots}
            compatible_slots = {c: set() for c in self.courses}

            for c in self.courses:
                sc = self.sched_courses.get(course=c)
                if not c.suspens:
                    slots = {slot for slot in slots_filter(self.courses_slots, week=c.week,
                                                           start_time=sc.start_time, course_type=c.type)
                             if slot.day.day == sc.day}
                    if len(slots) == 1:
                        sl = slots.pop()
                    else:
                        raise TypeError(f"There should one and only one slot for {c}, and we have {slots}...")
                    compatible_courses[sl].add(c)
                    compatible_slots[c] = {sl}
                else:
                    slots = set([slot for slot in slots_filter(self.courses_slots, week=c.week,
                                                               course_type=c.type)])
                    compatible_slots[c] = slots
                    for sl in slots:
                        compatible_courses[sl].add(c)
        return compatible_slots, compatible_courses

    def groups_init(self):
        # GROUPS
        groups = Group.objects.filter(train_prog__in=self.train_prog)

        basic_groups = groups.filter(basic=True)
        #  ,
        # id__in=self.courses.values_list('groupe_id').distinct())

        all_groups_of = {}
        for g in basic_groups:
            all_groups_of[g] = [g] + list(g.ancestor_groups())

        basic_groups_of = {}
        for g in groups:
            basic_groups_of = []
            for bg in basic_groups:
                if g in all_groups_of[bg]:
                    basic_groups_of.append(bg)

        courses_for_group = {}
        for g in groups:
            courses_for_group[g] = set(self.courses.filter(groups=g))

        courses_for_basic_group = {}
        for bg in basic_groups:
            courses_for_basic_group[bg] = set(self.courses.filter(groups__in=all_groups_of[bg]))

        return groups, basic_groups, all_groups_of, basic_groups_of, courses_for_group, courses_for_basic_group

    def users_init(self):
        # USERS

        instructors = set()
        for tutor in Tutor.objects.filter(id__in=self.courses.values_list('tutor_id')):
            instructors.add(tutor)
        for mpt in ModulePossibleTutors.objects.filter(module__in=self.modules):
            for tutor in mpt.possible_tutors.all():
                instructors.add(tutor)
        for cpt in CoursePossibleTutors.objects.filter(course__in=self.courses):
            for tutor in cpt.possible_tutors.all():
                instructors.add(tutor)
        for mtr in ModuleTutorRepartition.objects.filter(module__in=self.modules,
                                                         week__in=self.weeks):
            instructors.add(mtr.tutor)
        try:
            no_tut = Tutor.objects.get(username='---')
            instructors.add(no_tut)
        except:
            pass
        courses_for_tutor = {}
        for i in instructors:
            courses_for_tutor[i] = set(self.courses.filter(tutor=i))

        courses_for_supp_tutor = {}
        for i in instructors:
            courses_for_supp_tutor[i] = set(i.courses_as_supp.filter(id__in=self.courses))

        availabilities = {}
        for i in instructors:
            availabilities[i] = {}
            for week in self.weeks:
                availabilities[i][week] = set(UserPreference.objects.filter(week=week, user=i))
                if not availabilities[i][week]:
                    availabilities[i][week] = set(UserPreference.objects.filter(week=None, user=i))

        fixed_courses_for_tutor = {}
        for i in instructors:
            fixed_courses_for_tutor[i] = set(self.fixed_courses.filter(Q(tutor=i) | Q(course__supp_tutor=i)))

        other_departments_courses_for_tutor = {}
        for i in instructors:
            other_departments_courses_for_tutor[i] = set(self.other_departments_courses.filter(tutor=i))

        other_departments_scheduled_courses_for_supp_tutor = {}
        for i in instructors:
            other_departments_scheduled_courses_for_supp_tutor[i] = set(self.other_departments_sched_courses
                                                              .filter(course__supp_tutor=i))

        other_departments_scheduled_courses_for_tutor = {}
        for i in instructors:
            other_departments_scheduled_courses_for_tutor[i] = set(self.other_departments_sched_courses
                                                                   .filter(course__tutor=i))

        physical_presence_days_for_tutor = {}
        for i in instructors:
            physical_presence_days_for_tutor[i] = {}
            for w in self.weeks:
                physical_presence_days_for_tutor[i][w] = []
                if PhysicalPresence.objects.filter(user=i, week=w).exists():
                    for pp in i.physical_presences.filter(week=w):
                        physical_presence_days_for_tutor[i][w].append(pp.day)

        return instructors, courses_for_tutor, courses_for_supp_tutor, availabilities, \
            fixed_courses_for_tutor, other_departments_courses_for_tutor, \
            other_departments_scheduled_courses_for_supp_tutor, \
            other_departments_scheduled_courses_for_tutor, \
            physical_presence_days_for_tutor

    def possible_courses_tutor_init(self):
        possible_tutors = {}
        try:
            no_tut = Tutor.objects.get(username='---')
        except:
            no_tut = None
        for m in self.modules:
            if ModulePossibleTutors.objects.filter(module=m).exists():
                possible_tutors[m] = set(ModulePossibleTutors.objects.get(module=m).possible_tutors.all())
            else:
                possible_tutors[m] = self.instructors
        for c in self.courses:
            if c.tutor is not None:
                possible_tutors[c] = {c.tutor}
            elif CoursePossibleTutors.objects.filter(course=c).exists():
                possible_tutors[c] = set(CoursePossibleTutors.objects.get(course=c).possible_tutors.all())
            elif ModuleTutorRepartition.objects.filter(course_type=c.type, module=c.module,
                                                       week=c.week).exists():
                possible_tutors[c] = set(mtr.tutor for mtr in
                                         ModuleTutorRepartition.objects.filter(course_type=c.type, module=c.module,
                                                                               week=c.week))
                if no_tut is not None:
                    possible_tutors[c].add(no_tut)
            else:
                possible_tutors[c] = possible_tutors[c.module]

        possible_modules = {}
        for i in self.instructors:
            possible_modules[i] = set(m for m in self.modules
                                      if i in possible_tutors[m])

        possible_courses = {}
        for i in self.instructors:
            possible_courses[i] = set(c for c in self.courses if i in possible_tutors[c])

        return possible_tutors, possible_modules, possible_courses

    def visio_init(self):

        visio_courses = set()
        no_visio_courses = set()
        visio_ponderation = {c: 1 for c in self.courses}

        for course_additional in CourseAdditional.objects.filter(course__in=self.courses):
            vp = course_additional.visio_preference_value
            if vp == 0:
                no_visio_courses.add(course_additional.course)
            elif vp == 8:
                visio_courses.add(course_additional.course)
            else:
                visio_ponderation[course_additional.course] = vp / 4

        return visio_courses, no_visio_courses, visio_ponderation
