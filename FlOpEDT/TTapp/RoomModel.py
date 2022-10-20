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

from base.models import RoomPreference, ScheduledCourse, TimeGeneralSettings, RoomSort, Room, Course

from base.timing import Day
import base.queries as queries

from TTapp.slots import Slot

from django.db.models import F, Q

from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType

from core.decorators import timer

from TTapp.FlopModel import FlopModel, GUROBI_NAME, get_room_constraints
from TTapp.RoomConstraints.RoomConstraint import LocateAllCourses, \
    LimitGroupMoves, LimitTutorMoves, ConsiderRoomSorts
from TTapp.FlopConstraint import max_weight

from base.timing import  flopday_to_date, floptime_to_time

from roomreservation.models import RoomReservation


class RoomModel(FlopModel):
    @timer
    def __init__(self, department_abbrev, weeks, work_copy=0, keep_many_solution_files=False):
        # beg_file = os.path.join('logs',"FlOpTT")
        super(RoomModel, self).__init__(department_abbrev, weeks, keep_many_solution_files=keep_many_solution_files)

        print("\nLet's start rooms affectation for weeks #%s" % self.weeks)
        self.work_copy = work_copy
        self.scheduled_courses, self.courses, self.corresponding_scheduled_course, \
            self.courses_for_week = self.courses_init()
        self.days, self.slots = self.slots_init()
        self.other_departments_located_scheduled_courses, \
            self.other_departments_located_scheduled_courses_for_slot = self.other_departments_located_scheduled_courses_init()
        self.room_types, self.rooms, self.basic_rooms, self.rooms_for_type, \
            self.room_course_compat, self.course_room_compat, self.other_departments_located_scheduled_courses_for_room, \
            self.courses_for_room_type = self.rooms_init()
        self.tutors, self.courses_for_tutor, self.tutor_room_sorts, self.groups, self.basic_groups, \
            self.all_groups_of, self.basic_groups_of, self.structural_groups, \
            self.transversal_groups, self.courses_for_group, self.courses_for_basic_group = self.users_init()
        self.cost_I, self.cost_G, self.cost_SL, self.generic_cost = self.costs_init()
        self.TTrooms = self.TTrooms_init()
        self.avail_room = self.compute_avail_room()
        self.add_core_constraints()
        self.add_specific_constraints()
        if self.warnings:
            print("Relevant warnings :")
            for key, key_warnings in self.warnings.items():
                print("%s : %s" % (key, ", ".join([str(x) for x in key_warnings])))

    def solution_files_prefix(self):
        return f"room_model_{self.department.abbrev}_{'_'.join(str(w) for w in self.weeks)}"

    @timer
    def courses_init(self):
        scheduled_courses = ScheduledCourse.objects.filter(course__week__in=self.weeks,
                                                           work_copy=self.work_copy,
                                                           course__type__department=self.department)\
            .select_related('course')
        courses = Course.objects.filter(scheduledcourse__in=scheduled_courses).select_related('room_type')
        corresponding_scheduled_course = {}
        for scheduled_course in scheduled_courses:
            corresponding_scheduled_course[scheduled_course.course] = scheduled_course
        courses_for_week={}
        for week in self.weeks:
            courses_for_week[week] = set(courses.filter(week=week))
        return scheduled_courses, courses, corresponding_scheduled_course, courses_for_week

    @timer
    def slots_init(self):
        days = [Day(week=week, day=day)
                for week in self.weeks
                for day in TimeGeneralSettings.objects.get(department=self.department).days]

        slots = []
        for day in days:
            scheduled_courses_of_the_day = self.scheduled_courses.filter(course__week=day.week, day=day.day)
            if not scheduled_courses_of_the_day.exists():
                continue
            times_set = set(sc.start_time for sc in scheduled_courses_of_the_day) \
                        | set(sc.end_time for sc in scheduled_courses_of_the_day)
            times_list = list(times_set)
            times_list.sort()
            for i in range(len(times_list)-1):
                slots.append(Slot(day=day,
                                  start_time=times_list[i],
                                  end_time=times_list[i+1]))
        return days, slots

    @timer
    def other_departments_located_scheduled_courses_init(self):
        other_departments_located_scheduled_courses = \
            ScheduledCourse.objects.filter(course__week__in=self.weeks,
                                           work_copy=0)\
                .exclude(course__type__department=self.department)\
                .exclude(room=None)
        other_departments_located_scheduled_courses_for_slot = {}
        for sl in self.slots:
            other_departments_located_scheduled_courses_for_slot[sl] = \
                set(lc for lc in other_departments_located_scheduled_courses
                    if sl.is_simultaneous_to(lc))
        return other_departments_located_scheduled_courses, other_departments_located_scheduled_courses_for_slot

    @timer
    def users_init(self):
        # USERS
        tutors = set(c.tutor for c in self.scheduled_courses.distinct("tutor"))
        for course in self.courses.distinct("supp_tutor"):
            tutors |= set(course.supp_tutor.all())

        courses_for_tutor = {}
        for tutor in tutors:
            courses_for_tutor[tutor] = set(self.courses.filter(Q(tutor=tutor) | Q(supp_tutor=tutor)))

        tutor_room_sorts = {}
        for tutor in tutors:
            tutor_room_sorts[tutor] = RoomSort.objects.filter(for_type__department=self.department,
                                                              tutor=tutor)

        groups = set()
        for course in self.courses.distinct("groups"):
            groups |= set(course.groups.all())

        structural_groups = set(g.structuralgroup for g in groups if g.is_structural)
        transversal_groups = set(g.transversalgroup for g in groups if g.is_transversal)

        basic_groups = set()
        for g in structural_groups:
            basic_groups |= g.basic_groups()

        all_groups_of = {}
        for g in basic_groups:
            all_groups_of[g] = g.and_ancestors()

        basic_groups_of = {}
        for g in structural_groups:
            basic_groups_of[g] = set()
            for bg in basic_groups:
                if g in all_groups_of[bg]:
                    basic_groups_of[g].add(bg)

        courses_for_group = {}
        for g in groups:
            courses_for_group[g] = set(self.courses.filter(groups=g))

        courses_for_basic_group = {}
        for bg in basic_groups:
            courses_for_basic_group[bg] = set(self.courses.filter(groups__in=all_groups_of[bg]))

        return tutors, courses_for_tutor, tutor_room_sorts, groups, basic_groups, all_groups_of, \
               basic_groups_of, structural_groups, transversal_groups, courses_for_group, courses_for_basic_group

    @timer
    def rooms_init(self):
        # ROOMS
        room_types = set(c.room_type for c in self.courses.distinct('room_type'))

        basic_rooms = queries.get_rooms(self.department.abbrev, basic=True).distinct()
        rooms_for_type = {t: t.members.all() for t in room_types}

        rooms = set(Room.objects.filter(departments=self.department).distinct())
        for room in basic_rooms:
            rooms |= room.and_overrooms()

        course_room_compat = {}
        for course in self.courses:
            course_room_compat[course] = set(course.room_type.members.all())

        # for each basic room, build the list of courses that may use it, in couple with the corresponding room
        room_course_compat = {}
        for basic_room in basic_rooms:
            room_course_compat[basic_room] = []
            for room in basic_room.and_overrooms():
                room_course_compat[basic_room].extend(
                    [(course, room) for course in self.courses if room in course_room_compat[course]])

        if self.department.mode.visio:
            for c in self.courses:
                course_room_compat[c].add(None)

        other_departments_located_scheduled_courses_for_room = {}
        for basic_room in basic_rooms:
            other_departments_located_scheduled_courses_for_room[basic_room] = set()
            for room in basic_room.and_overrooms():
                other_departments_located_scheduled_courses_for_room[basic_room] \
                    |= set(self.other_departments_located_scheduled_courses.filter(room=room))

        courses_for_room_type = {}
        for rt in room_types:
            courses_for_room_type[rt] = set(self.courses.filter(room_type=rt))

        return room_types, rooms, basic_rooms, rooms_for_type, room_course_compat, course_room_compat, \
               other_departments_located_scheduled_courses_for_room, courses_for_room_type

    @timer
    def TTrooms_init(self):
        TTrooms = {}
        for course in self.courses:
            for room in self.course_room_compat[course]:
                TTrooms[(course, room)] = self.add_var("TTroom(%s,%s)" % (course, room))
        return TTrooms

    @timer
    def compute_avail_room(self):
        avail_room = {}
        for room in self.basic_rooms:
            avail_room[room] = {}
            for sl in self.slots:
                if RoomPreference.objects.filter(
                        start_time__lt=sl.start_time + sl.duration,
                        start_time__gt=sl.start_time - F('duration'),
                        day=sl.day.day,
                        week=sl.day.week,
                        room=room, value=0).exists():
                    avail_room[room][sl] = 0
                elif RoomReservation.objects.filter(
                        start_time__lt=floptime_to_time(sl.start_time + sl.duration),
                        end_time__gt=floptime_to_time(sl.start_time),
                        date=flopday_to_date(sl.day),
                        room=room).exists():
                    avail_room[room][sl] = 0
                else:
                    avail_room[room][sl] = 1

        for sl in self.slots:
            # constraint : other_departments_located_courses rooms are not available
            for basic_room in self.basic_rooms:
                other_dep_located_scheduled_courses = \
                    self.other_departments_located_scheduled_courses_for_room[basic_room] \
                    & self.other_departments_located_scheduled_courses_for_slot[sl]
                if other_dep_located_scheduled_courses:
                    avail_room[basic_room][sl] = 0
        return avail_room

    @timer
    def costs_init(self):
        cost_I = dict(list(zip(self.tutors,
                               [{week: self.lin_expr() for week in self.weeks + [None]} for _ in
                                self.tutors])))

        cost_G = dict(
            list(zip(self.basic_groups,
                     [{week: self.lin_expr() for week in self.weeks + [None]} for _ in self.basic_groups])))

        cost_SL = dict(
            list(zip(self.slots,
                     [self.lin_expr() for _ in self.slots])))

        generic_cost = {week: self.lin_expr() for week in self.weeks + [None]}

        return cost_I, cost_G, cost_SL, generic_cost

    def add_to_slot_cost(self, slot, cost):
        self.cost_SL[slot] += cost

    def add_to_inst_cost(self, instructor, cost, week=None):
        self.cost_I[instructor][week] += cost

    def add_to_group_cost(self, group, cost, week=None):
        self.cost_G[group][week] += cost

    def add_to_generic_cost(self, cost, week=None):
        self.generic_cost[week] += cost

    @timer
    def add_core_constraints(self):
        # constraint : each Room is used at most once, if available, on every slot
        for basic_room in self.basic_rooms:
            for sl in self.slots:
                self.add_constraint(self.sum(self.TTrooms[(course, room)]
                                             for (course, room) in self.room_course_compat[basic_room]
                                             if sl.is_simultaneous_to(self.corresponding_scheduled_course[course])),
                                    '<=', self.avail_room[basic_room][sl],
                                    Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                               rooms=basic_room, slots=sl))

        # each course is located into a room
        if not LocateAllCourses.objects.filter(department=self.department).exists():
            LocateAllCourses.objects.create(department=self.department)

        # limit groups moves
        if not LimitGroupMoves.objects.filter(department=self.department).exists():
            LimitGroupMoves.objects.create(department=self.department, weight=max_weight)

        # limit tutors moves
        if not LimitTutorMoves.objects.filter(department=self.department).exists():
            LimitTutorMoves.objects.create(department=self.department, weight=max_weight)

        # consider room sort
        if not ConsiderRoomSorts.objects.filter(department=self.department).exists():
            ConsiderRoomSorts.objects.create(department=self.department, weight=max_weight)

    def add_specific_constraints(self):
        """
        Add the active specific constraints stored in the database.
        """
        for week in self.weeks:
            for constr in get_room_constraints(
                    self.department,
                    week=week,
                    is_active=True):
                print(constr.__class__.__name__, constr.id, end=' - ')
                timer(constr.enrich_room_model)(self, week)

    def update_objective(self):
        self.obj = self.lin_expr()
        for week in self.weeks + [None]:
            for i in self.tutors:
                self.obj += self.cost_I[i][week]
            for g in self.basic_groups:
                self.obj += self.cost_G[g][week]
            self.obj += self.generic_cost[week]
        for sl in self.slots:
            self.obj += self.cost_SL[sl]
        self.set_objective(self.obj)


    def solve(self, time_limit=None, solver=GUROBI_NAME, threads=None, ignore_sigint=False, create_new_work_copy=False):
        """
        Generates a schedule from the TTModel
        The solver stops either when the best schedule is obtained or timeLimit
        is reached.

        If stabilize_work_copy is None: does not move the scheduled courses
        whose group is not in train_prog and fetches from the remote database
        these scheduled courses with work copy 0.

        If target_work_copy is given, stores the resulting schedule under this
        work copy number.
        If target_work_copy is not given, stores under the lowest working copy
        number that is greater than the maximum work copy numbers for the
        considered week.
        Returns the number of the work copy
        """
        print("\nLet's solve weeks #%s" % self.weeks)

        self.update_objective()

        result = self.optimize(time_limit, solver, threads=threads, ignore_sigint=ignore_sigint)

        if result is not None:
            result_work_copy = self.add_rooms_in_db(create_new_work_copy)
            return result_work_copy

    def add_rooms_in_db(self, create_new_work_copy):
        if create_new_work_copy:
            target_work_copy = self.choose_free_work_copy()
        else:
            target_work_copy = self.work_copy
        course_location_list = []
        for course in self.courses:
            for room in self.course_room_compat[course]:
                if self.get_var_value(self.TTrooms[(course, room)]) == 1:
                    course_location_list.append((course, room))
        for course, room in course_location_list:
            scheduled_course = self.corresponding_scheduled_course[course]
            if create_new_work_copy:
                scheduled_course.pk = None
                scheduled_course.work_copy = target_work_copy
            scheduled_course.room = room
            scheduled_course.save()
        return target_work_copy