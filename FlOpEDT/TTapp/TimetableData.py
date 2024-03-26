#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime as dt
import logging

from django.db.models import Q

import base.queries as queries
from base.models import (
    Course,
    CourseAdditional,
    CourseAvailability,
    CoursePossibleTutors,
    CourseStartTimeConstraint,
    Dependency,
    Holiday,
    Module,
    ModulePossibleTutors,
    ModuleTutorRepartition,
    Pivot,
    Room,
    RoomPonderation,
    RoomSort,
    RoomType,
    ScheduledCourse,
    StructuralGroup,
    TimeGeneralSettings,
    TrainingHalfDay,
    TransversalGroup,
)
from base.models.availability import period_actual_availabilities

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
from base.timing import add_duration_to_time, get_default_date
from misc.manage_rooms_ponderations import register_ponderations_in_database
from people.models import PhysicalPresence, Tutor
from TTapp.models import AssignAllCourses
from TTapp.slots import CourseSlot, Slot, days_filter, slots_filter

logger = logging.getLogger(__name__)
pattern = r".+: (.|\s)+ (=|>=|<=) \d*"
GUROBI = "GUROBI"
GUROBI_NAME = "GUROBI_CMD"


class TimetableData(object):
    def __init__(self, department, periods, train_prog, slots_step=None):
        self.train_prog = train_prog
        self.department = department
        self.periods = periods
        self.slots_step = slots_step
        self.possible_apms = set()
        (
            self.days,
            self.day_after,
            self.holidays,
            self.training_half_days,
            self.day_before,
        ) = self.days_init()
        self.dates = self.days
        (
            self.course_types,
            self.courses,
            self.courses_by_period,
            self.sched_courses,
            self.fixed_courses,
            self.other_departments_courses,
            self.other_departments_sched_courses,
            self.courses_availabilities,
            self.modules,
            self.dependencies,
            self.pivots,
        ) = self.courses_init()
        (
            self.courses_slots,
            self.availability_slots,
            self.first_hour_slots,
            self.last_hour_slots,
        ) = self.slots_init()
        (
            self.fixed_courses_for_avail_slot,
            self.other_departments_sched_courses_for_avail_slot,
        ) = self.courses_for_avail_slot_init()
        if self.department.mode.visio:
            (
                self.visio_courses,
                self.no_visio_courses,
                self.visio_ponderation,
            ) = self.visio_init()
        (
            self.room_types,
            self.used_room_types,
            self.rooms,
            self.basic_rooms,
            self.room_prefs,
            self.rooms_for_type,
            self.room_course_compat,
            self.course_rg_compat,
            self.fixed_courses_for_room,
            self.other_departments_sched_courses_for_room,
            self.rooms_ponderations,
            self.courses_for_room_type,
        ) = self.rooms_init()
        self.compatible_slots, self.compatible_courses = self.compatibilities_init()
        (
            self.groups,
            self.transversal_groups,
            self.all_groups,
            self.basic_groups,
            self.all_groups_of,
            self.basic_groups_of,
            self.conflicting_basic_groups,
            self.transversal_groups_of,
            self.not_parallel_transversal_groups,
            self.courses_for_group,
            self.courses_for_basic_group,
            self.all_courses_for_basic_group,
        ) = self.groups_init()
        (
            self.instructors,
            self.courses_for_tutor,
            self.courses_for_supp_tutor,
            self.availabilities,
            self.fixed_courses_for_tutor,
            self.other_departments_courses_for_tutor,
            self.other_departments_scheduled_courses_for_supp_tutor,
            self.other_departments_scheduled_courses_for_tutor,
            self.physical_presence_days_for_tutor,
        ) = self.users_init()
        (
            self.possible_tutors,
            self.possible_modules,
            self.possible_courses,
        ) = self.possible_courses_tutor_init()

    def days_init(self):
        all_days = set()
        for period in self.periods:
            all_days |= set(period.dates())
        days = list(
            days_filter(
                all_days,
                weekday_in=TimeGeneralSettings.objects.get(
                    department=self.department
                ).days,
            )
        )
        days.sort()

        training_half_days = TrainingHalfDay.objects.filter(
            date__in=days, train_prog__in=self.train_prog
        )

        database_holidays = Holiday.objects.filter(date__in=days)
        holidays = set(d.date for d in database_holidays)

        if self.department.mode.cosmo != 1:
            for hd in holidays:
                days.remove(hd.date)

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
                day_before[day] = days[i - 1]

        days = set(days)

        return days, day_after, holidays, training_half_days, day_before

    def slots_init(self):
        # SLOTS
        print("Slot tools definition", end=", ")
        tgs = TimeGeneralSettings.objects.get(department=self.department)
        courses_slots = set()
        filtered_cstc = CourseStartTimeConstraint.objects.filter(
            department=self.department
        )
        # Courses slots
        for cc in filtered_cstc:
            start_times = cc.allowed_start_times
            if self.slots_step is None:
                courses_slots |= set(
                    CourseSlot(
                        dt.datetime.combine(d, start_time), cc.duration, self.department
                    )
                    for d in self.days
                    for start_time in start_times
                )
            else:
                courses_slots |= set(
                    CourseSlot(
                        dt.datetime.combine(d, start_time), cc.duration, self.department
                    )
                    for d in self.days
                    for start_time in cc.allowed_start_times
                    if start_time % self.slots_step == 0
                )
        # We remove the course slots that are inside the lunch break
        courses_slots_to_remove = set()
        for course_slot in courses_slots:
            if (
                course_slot.start_time.time() < tgs.afternoon_start_time
                and course_slot.end_time.time() > tgs.morning_end_time
            ):
                courses_slots_to_remove.add(course_slot)
        courses_slots -= courses_slots_to_remove

        for slot in courses_slots:
            self.possible_apms.add(slot.apm)

        # We build availability slots considering the possible Intervals from a possible start time to another
        # and adding the possible end times. It is a partition, and we may use the Partition class to do it.
        dayly_availability_slots = set()
        for cst in filtered_cstc:
            dayly_availability_slots |= set(cst.allowed_start_times)

            dayly_availability_slots |= set(
                add_duration_to_time(st, cst.duration) for st in cst.allowed_start_times
            )
        dayly_availability_slots.add(tgs.day_end_time)
        dayly_availability_slots = list(dayly_availability_slots)
        dayly_availability_slots.sort()
        start_times = dayly_availability_slots[:-1]
        end_times = dayly_availability_slots[1:]
        if (
            tgs.morning_end_time < tgs.afternoon_start_time
            and tgs.morning_end_time in start_times
            and tgs.afternoon_start_time in end_times
        ):
            start_times.remove(tgs.morning_end_time)
            end_times.remove(tgs.afternoon_start_time)
            # We remove the slots that are inside the lunch break
            for st in dayly_availability_slots:
                if tgs.morning_end_time < st < tgs.afternoon_start_time:
                    start_times.remove(st)
                    end_times.remove(st)

        availability_slots = {
            Slot(
                start_time=dt.datetime.combine(day, start_times[i]),
                end_time=dt.datetime.combine(day, end_times[i]),
            )
            for day in self.days
            for i in range(len(start_times))
        }
        print(
            "Ok"
            + f" : {len(courses_slots)} courses_slots and {len(availability_slots)} availability_slots created!"
        )

        first_hour_slots = {
            slot
            for slot in availability_slots
            if slot.start_time.time()
            < add_duration_to_time(start_times[0], dt.timedelta(minutes=60))
        }

        last_hour_slots = {
            slot
            for slot in availability_slots
            if slot.end_time.time()
            > add_duration_to_time(end_times[-1], dt.timedelta(minutes=60))
        }

        return courses_slots, availability_slots, first_hour_slots, last_hour_slots

    def courses_init(self):
        # COURSES
        courses = Course.objects.filter(
            period__in=self.periods, module__train_prog__in=self.train_prog
        ).select_related("module", "room_type")

        course_types = set(c.type for c in courses)

        courses_by_period = {
            period: set(courses.filter(period=period)) for period in self.periods
        }

        sched_courses = ScheduledCourse.objects.filter(course__in=courses)

        if self.department.mode.cosmo:
            sched_courses = sched_courses.filter(version__major=0)

        fixed_courses = ScheduledCourse.objects.filter(
            course__module__train_prog__department=self.department,
            course__period__in=self.periods,
            version__major=0,
        ).exclude(course__module__train_prog__in=self.train_prog)

        other_departments_courses = Course.objects.filter(
            period__in=self.periods
        ).exclude(type__department=self.department)

        other_departments_sched_courses = ScheduledCourse.objects.filter(
            course__in=other_departments_courses, version__major=0
        )

        courses_availabilities = set()
        for date in self.days:
            dated_availabilities = CourseAvailability.objects.filter(
                date=date, train_prog__department=self.department
            )
            if dated_availabilities.exists():
                courses_availabilities |= set(dated_availabilities)
            else:
                default_date = get_default_date(date)
                courses_availabilities |= set(
                    CourseAvailability.objects.filter(
                        date=default_date, train_prog__department=self.department
                    )
                )

        modules = Module.objects.filter(
            id__in=courses.values_list("module_id").distinct()
        )

        dependencies = Dependency.objects.filter(
            course1__period__in=self.periods,
            course2__period__in=self.periods,
            course1__module__train_prog__in=self.train_prog,
        )

        pivots = Pivot.objects.filter(
            pivot_course__period__in=self.periods,
            other_courses__period__in=self.periods,
            pivot_course__module__train_prog__in=self.train_prog,
        )

        return (
            course_types,
            courses,
            courses_by_period,
            sched_courses,
            fixed_courses,
            other_departments_courses,
            other_departments_sched_courses,
            courses_availabilities,
            modules,
            dependencies,
            pivots,
        )

    def courses_for_avail_slot_init(self):
        fixed_courses_for_avail_slot = {}
        for sl in self.availability_slots:
            fixed_courses_for_avail_slot[sl] = set(
                fc for fc in self.fixed_courses if sl.is_simultaneous_to(fc)
            )

        other_departments_sched_courses_for_avail_slot = {}
        for sl in self.availability_slots:
            other_departments_sched_courses_for_avail_slot[sl] = set(
                fc
                for fc in self.other_departments_sched_courses
                if fc.start_time < sl.end_time and sl.start_time < fc.end_time
            )

        return (
            fixed_courses_for_avail_slot,
            other_departments_sched_courses_for_avail_slot,
        )

    def rooms_init(self):
        # ROOMS
        room_types = RoomType.objects.filter(department=self.department)
        used_room_types = set(c.room_type for c in self.courses.distinct("room_type"))
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
                    [(c, rg) for c in self.courses if rg in course_rg_compat[c]]
                )
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
                other_departments_sched_courses_for_room[r] |= set(
                    self.other_departments_sched_courses.filter(room=rg)
                )

        department_rooms_ponderations = RoomPonderation.objects.filter(
            department=self.department
        )
        if not department_rooms_ponderations.exists():
            register_ponderations_in_database(self.department)

        rooms_ponderations = set(
            rp
            for rp in department_rooms_ponderations
            if rp.get_room_types_set() & set(used_room_types)
        )

        courses_for_room_type = {}
        for rt in room_types:
            courses_for_room_type[rt] = set(self.courses.filter(room_type=rt))

        return (
            room_types,
            used_room_types,
            rooms,
            basic_rooms,
            room_prefs,
            rooms_for_type,
            room_course_compat,
            course_rg_compat,
            fixed_courses_for_room,
            other_departments_sched_courses_for_room,
            rooms_ponderations,
            courses_for_room_type,
        )

    def compatibilities_init(self):
        # COMPATIBILITY
        # Slots and courses are compatible if they have the same type
        # OR if slot type is None and they have the same duration
        if not self.department.mode.cosmo:
            compatible_slots = {}
            for c in self.courses:
                compatible_slots[c] = slots_filter(
                    self.courses_slots,
                    period=c.period,
                    duration=c.duration,
                    department=c.type.department,
                )

            compatible_courses = {}
            for sl in self.courses_slots:
                compatible_courses[sl] = set(
                    course
                    for course in self.courses
                    if course.duration == sl.duration
                    and sl.date in course.period.dates()
                    and sl.department == course.type.department
                )
        else:
            compatible_courses = {sl: set() for sl in self.courses_slots}
            compatible_slots = {c: set() for c in self.courses}

            for c in self.courses:
                sc = self.sched_courses.get(course=c)
                if not c.suspens:
                    slots = {
                        slot
                        for slot in slots_filter(
                            self.courses_slots,
                            start_time=sc.start_time,
                            duration=c.duration,
                            department=c.type.department,
                        )
                    }
                    if len(slots) == 1:
                        sl = slots.pop()
                    else:
                        raise TypeError(
                            f"There should one and only one slot for {c}, and we have {slots}..."
                        )
                    compatible_courses[sl].add(c)
                    compatible_slots[c] = {sl}
                else:
                    slots = set(
                        [
                            slot
                            for slot in slots_filter(
                                self.courses_slots,
                                period=c.period,
                                duration=c.duration,
                                department=c.type.department,
                            )
                        ]
                    )
                    compatible_slots[c] = slots
                    for sl in slots:
                        compatible_courses[sl].add(c)
        return compatible_slots, compatible_courses

    def groups_init(self):
        # GROUPS
        structural_groups = StructuralGroup.objects.filter(
            train_prog__in=self.train_prog
        )
        transversal_groups = TransversalGroup.objects.filter(
            train_prog__in=self.train_prog
        )
        all_groups = set(structural_groups) | set(transversal_groups)

        basic_groups = structural_groups.filter(basic=True)
        #  ,
        # id__in=self.courses.values_list('groupe_id').distinct())

        all_groups_of = {}
        for g in basic_groups:
            all_groups_of[g] = g.and_ancestors()

        basic_groups_of = {}
        for g in structural_groups:
            basic_groups_of[g] = set()
            for bg in basic_groups:
                if g in all_groups_of[bg]:
                    basic_groups_of[g].add(bg)

        conflicting_basic_groups = {}
        for tg in transversal_groups:
            conflicting_basic_groups[tg] = set()
            for cg in tg.conflicting_groups.all():
                conflicting_basic_groups[tg] |= basic_groups_of[cg]

        transversal_groups_of = {}
        for bg in basic_groups:
            transversal_groups_of[bg] = set()
            for tg in transversal_groups:
                if bg in conflicting_basic_groups[tg]:
                    transversal_groups_of[bg].add(tg)

        not_parallel_transversal_groups = {}
        for tg in transversal_groups:
            not_parallel_transversal_groups[tg] = set()
            for tg2 in transversal_groups.filter(train_prog=tg.train_prog).exclude(
                id=tg.id
            ):
                if (
                    tg2 not in tg.parallel_groups.all()
                    and conflicting_basic_groups[tg] & conflicting_basic_groups[tg2]
                ):
                    not_parallel_transversal_groups[tg].add(tg2)

        courses_for_group = {}
        for g in all_groups:
            courses_for_group[g] = set(self.courses.filter(groups=g))

        courses_for_basic_group = {}
        for bg in basic_groups:
            courses_for_basic_group[bg] = set(
                self.courses.filter(groups__in=all_groups_of[bg])
            )

        # consider all courses, including transversal_groups ones
        all_courses_for_basic_group = {}
        for bg in basic_groups:
            # the "set" function is called inorder to make a copy!
            all_courses_for_basic_group[bg] = set(courses_for_basic_group[bg])
            for tg in transversal_groups_of[bg]:
                all_courses_for_basic_group[bg] |= courses_for_group[tg]

        return (
            structural_groups,
            transversal_groups,
            all_groups,
            basic_groups,
            all_groups_of,
            basic_groups_of,
            conflicting_basic_groups,
            transversal_groups_of,
            not_parallel_transversal_groups,
            courses_for_group,
            courses_for_basic_group,
            all_courses_for_basic_group,
        )

    def users_init(self):
        # USERS
        instructors = set()
        for tutor in Tutor.objects.filter(id__in=self.courses.values_list("tutor_id")):
            instructors.add(tutor)
        for cst in self.courses.distinct("supp_tutor"):
            for tutor in cst.supp_tutor.all():
                instructors.add(tutor)
        for mpt in ModulePossibleTutors.objects.filter(module__in=self.modules):
            for tutor in mpt.possible_tutors.all():
                instructors.add(tutor)
        for cpt in CoursePossibleTutors.objects.filter(course__in=self.courses):
            for tutor in cpt.possible_tutors.all():
                instructors.add(tutor)
        for mtr in ModuleTutorRepartition.objects.filter(
            module__in=self.modules, period__in=self.periods
        ):
            instructors.add(mtr.tutor)
        try:
            no_tut = Tutor.objects.get(username="---")
            instructors.add(no_tut)
        except:
            pass
        courses_for_tutor = {}
        for i in instructors:
            courses_for_tutor[i] = set(self.courses.filter(tutor=i))

        courses_for_supp_tutor = {}
        for i in instructors:
            courses_for_supp_tutor[i] = set(
                i.courses_as_supp.filter(id__in=self.courses)
            )

        availabilities = {}
        for i in instructors:
            availabilities[i] = {}
            for period in self.periods:
                availabilities[i][period] = period_actual_availabilities(i, period)

        fixed_courses_for_tutor = {}
        for i in instructors:
            fixed_courses_for_tutor[i] = set(
                self.fixed_courses.filter(Q(tutor=i) | Q(course__supp_tutor=i))
            )

        other_departments_courses_for_tutor = {}
        for i in instructors:
            other_departments_courses_for_tutor[i] = set(
                self.other_departments_courses.filter(tutor=i)
            )

        other_departments_scheduled_courses_for_supp_tutor = {}
        for i in instructors:
            other_departments_scheduled_courses_for_supp_tutor[i] = set(
                self.other_departments_sched_courses.filter(course__supp_tutor=i)
            )

        other_departments_scheduled_courses_for_tutor = {}
        for i in instructors:
            other_departments_scheduled_courses_for_tutor[i] = set(
                self.other_departments_sched_courses.filter(course__tutor=i)
            )

        physical_presence_days_for_tutor = {}
        for i in instructors:
            physical_presence_days_for_tutor[i] = {}
            for date in self.dates:
                if PhysicalPresence.objects.filter(user=i, date=date).exists():
                    physical_presence_days_for_tutor[i](date)

        return (
            instructors,
            courses_for_tutor,
            courses_for_supp_tutor,
            availabilities,
            fixed_courses_for_tutor,
            other_departments_courses_for_tutor,
            other_departments_scheduled_courses_for_supp_tutor,
            other_departments_scheduled_courses_for_tutor,
            physical_presence_days_for_tutor,
        )

    def possible_courses_tutor_init(self):
        possible_tutors = {}
        for m in self.modules:
            if ModulePossibleTutors.objects.filter(module=m).exists():
                possible_tutors[m] = set(
                    ModulePossibleTutors.objects.get(module=m).possible_tutors.all()
                )
            else:
                possible_tutors[m] = self.instructors

        no_tutor_courses = set()
        pre_assign_only_constraints = AssignAllCourses.objects.filter(
            Q(periods__in=self.periods) | Q(periods__isnull=True),
            department=self.department,
            pre_assigned_only=True,
        )
        if pre_assign_only_constraints.exists():
            for constraint in pre_assign_only_constraints:
                for period in self.periods:
                    no_tutor_courses |= constraint.no_tutor_courses(period, self)

        for c in no_tutor_courses:
            possible_tutors[c] = set()

        for c in set(self.courses) - no_tutor_courses:
            if c.tutor is not None:
                possible_tutors[c] = {c.tutor}
            else:
                if CoursePossibleTutors.objects.filter(course=c).exists():
                    possible_tutors[c] = set(
                        CoursePossibleTutors.objects.get(course=c).possible_tutors.all()
                    )
                elif ModuleTutorRepartition.objects.filter(
                    course_type=c.type, module=c.module, period=c.period
                ).exists():
                    possible_tutors[c] = set(
                        mtr.tutor
                        for mtr in ModuleTutorRepartition.objects.filter(
                            course_type=c.type, module=c.module, period=c.period
                        )
                    )
                else:
                    possible_tutors[c] = possible_tutors[c.module]

        possible_modules = {}
        for i in self.instructors:
            possible_modules[i] = set(
                m for m in self.modules if i in possible_tutors[m]
            )

        possible_courses = {}
        for i in self.instructors:
            possible_courses[i] = set(
                c for c in self.courses if i in possible_tutors[c]
            )

        return possible_tutors, possible_modules, possible_courses

    def visio_init(self):
        visio_courses = set()
        no_visio_courses = set()
        visio_ponderation = {c: 1 for c in self.courses}

        for course_additional in CourseAdditional.objects.filter(
            course__in=self.courses
        ):
            vp = course_additional.visio_preference_value
            if vp == 0:
                no_visio_courses.add(course_additional.course)
            elif vp == 8:
                visio_courses.add(course_additional.course)
            else:
                visio_ponderation[course_additional.course] = vp / 4

        return visio_courses, no_visio_courses, visio_ponderation
