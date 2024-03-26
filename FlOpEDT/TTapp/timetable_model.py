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

import datetime as dt

from django.core.mail import EmailMessage
from django.db import close_old_connections
from django.db.models import F
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from base.models import (
    GroupCost,
    GroupFreeHalfDay,
    ModuleTutorRepartition,
    RoomAvailability,
    RoomType,
    ScheduledCourse,
    ScheduledCourseAdditional,
    TimeGeneralSettings,
    TimetableVersion,
    TrainingProgramme,
    TutorCost,
)
from base.timing import Time
from core.decorators import timer
from people.models import Tutor
from roomreservation.models import RoomReservation
from TTapp.flop_constraint import MAX_WEIGHT
from TTapp.flop_model import (
    GUROBI_NAME,
    FlopModel,
    get_room_constraints,
    get_ttconstraints,
    iis_files_path,
)
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraints.course_constraint import CourseConstraint
from TTapp.ilp_constraints.constraints.slot_instructor_constraint import (
    SlotInstructorConstraint,
)
from TTapp.models import (
    AssignAllCourses,
    ConsiderDependencies,
    ConsiderModuleTutorRepartitions,
    ConsiderPivots,
    ConsiderTutorsUnavailability,
    MinGroupsHalfDays,
    MinimizeTutorsBusyDays,
    MinNonPreferedTrainProgsSlot,
    MinNonPreferedTutorsSlot,
    NoSimultaneousGroupCourses,
    RespectTutorsMaxTimePerDay,
    RespectTutorsMinTimePerDay,
    ScheduleAllCourses,
    StabilizeGroupsCourses,
    StabilizeTutorsCourses,
)
from TTapp.RoomConstraints.room_constraint import (
    LimitSimultaneousRoomCourses,
    LocateAllCourses,
)
from TTapp.room_model import RoomModel
from TTapp.slots import days_filter, slots_filter
from TTapp.timetable_data import TimetableData
from TTapp.timetable_utils import number_courses, print_differences


class TimetableModel(FlopModel):
    @timer
    def __init__(
        self,
        department_abbrev,
        periods,
        train_prog=None,
        major_to_stabilize=None,
        min_nps_i=1.0,
        min_bhd_g=1.0,
        min_bd_i=1.0,
        min_bhd_i=1.0,
        min_nps_c=1.0,
        max_stab=5.0,
        lim_ld=1.0,
        core_only=False,
        send_mails=False,
        slots_step=None,
        keep_many_solution_files=False,
        min_visio=0.5,
        pre_assign_rooms=False,
        post_assign_rooms=True,
    ):
        # beg_file = os.path.join('logs',"FlOpTT")
        super().__init__(
            department_abbrev,
            periods,
            keep_many_solution_files=keep_many_solution_files,
        )
        # Create the PuLP model, giving the name of the lp file
        self.min_ups_i = min_nps_i
        self.min_bhd_g = min_bhd_g
        self.min_bd_i = min_bd_i
        self.min_bhd_i = min_bhd_i
        self.min_ups_c = min_nps_c
        self.max_stab = max_stab
        self.lim_ld = lim_ld
        self.core_only = core_only
        self.send_mails = send_mails
        self.slots_step = slots_step
        self.min_visio = min_visio
        self.pre_assign_rooms = pre_assign_rooms
        self.post_assign_rooms = post_assign_rooms
        print(_(f"\nLet's start periods #{[period.name for period in self.periods]}"))
        assignment_text = ""
        if self.pre_assign_rooms:
            assignment_text += "pre"
            if self.post_assign_rooms:
                assignment_text += " & post"
        elif self.post_assign_rooms:
            assignment_text += "post"
        else:
            assignment_text += "no"
        print(_("Rooms assignment :"), assignment_text)

        if train_prog is None:
            train_prog = TrainingProgramme.objects.filter(department=self.department)
        else:
            try:
                iter(train_prog)
            except TypeError:
                train_prog = TrainingProgramme.objects.filter(id=train_prog.id)
            print(_(f"Will modify only courses of training programme(s) {train_prog}"))
        self.train_prog = train_prog
        self.major_to_stabilize = major_to_stabilize
        self.data = self.data_init()
        self.courses = self.data.courses
        self.possible_apms = self.data.possible_apms
        (
            self.tutor_cost,
            self.group_free_halfday,
            self.group_cost,
            self.slot_cost,
            self.generic_cost,
        ) = self.costs_init()
        self.scheduled, self.assigned = self.schedule_vars_init()
        if self.pre_assign_rooms:
            self.located = self.room_vars_init()
        (
            self.tutor_busy_day,
            self.tutor_busy_day_gte,
            self.tutor_busy_halfday,
            self.group_busy_day,
            self.group_busy_halfday,
            self.tutor_busy_slot,
            self.forced_tutor_busy_day,
        ) = self.busy_vars_init()
        if self.pre_assign_rooms:
            if self.department.mode.visio:
                self.physical_presence, self.has_visio = self.visio_vars_init()
        (
            self.avail_instr,
            self.avail_at_school_instr,
            self.unp_slot_cost,
        ) = self.compute_non_preferred_slots_cost()
        (
            self.unp_slot_cost_course,
            self.avail_course,
        ) = self.compute_non_preferred_slots_cost_course()
        self.avail_room = self.compute_avail_room()

        # Hack : permet que ça marche même si les dispos sur la base sont pas complètes
        for i in self.data.instructors:
            for availability_slot in self.data.availability_slots:
                if availability_slot not in self.avail_instr[i]:
                    self.avail_instr[i][availability_slot] = 0
                if availability_slot not in self.unp_slot_cost[i]:
                    self.unp_slot_cost[i][availability_slot] = 0

        self.add_aschedule_constraints()

        if self.warnings:
            print(_("Relevant warnings :"))
            for key, key_warnings in self.warnings.items():
                print(f"{key} : {', '.join([str(x) for x in key_warnings])}")

        if self.send_mails:
            self.send_lack_of_availability_mail()

        if not self.data.courses.exists():
            print("There are no course to be scheduled...")
            return

    @timer
    def data_init(self):
        data = TimetableData(
            self.department, self.periods, self.train_prog, self.slots_step
        )
        return data

    @timer
    def costs_init(self):
        tutor_cost = dict(
            list(
                zip(
                    self.data.instructors,
                    [
                        {period: self.lin_expr() for period in self.periods + [None]}
                        for _ in self.data.instructors
                    ],
                )
            )
        )
        group_free_half_day = {}
        for apm in self.possible_apms:
            group_free_half_day[apm] = dict(
                list(
                    zip(
                        self.data.basic_groups,
                        [
                            {period: self.lin_expr() for period in self.periods}
                            for _ in self.data.basic_groups
                        ],
                    )
                )
            )

        group_cost = dict(
            list(
                zip(
                    self.data.basic_groups,
                    [
                        {period: self.lin_expr() for period in self.periods + [None]}
                        for _ in self.data.basic_groups
                    ],
                )
            )
        )

        slot_cost = dict(
            list(
                zip(
                    self.data.courses_slots,
                    [self.lin_expr() for _ in self.data.courses_slots],
                )
            )
        )

        generic_cost = {period: self.lin_expr() for period in self.periods + [None]}

        return tutor_cost, group_free_half_day, group_cost, slot_cost, generic_cost

    @timer
    def schedule_vars_init(self):
        scheduled = {}
        assigned = {}

        for sl in self.data.courses_slots:
            for c in self.data.compatible_courses[sl]:
                scheduled[(sl, c)] = self.add_var(f"scheduled({sl},{c})")
                for i in self.data.possible_tutors[c]:
                    assigned[(sl, c, i)] = self.add_var(f"assigned({sl},{c},{i})")
        return scheduled, assigned

    @timer
    def room_vars_init(self):
        located = {}
        for sl in self.data.courses_slots:
            for c in self.data.compatible_courses[sl]:
                for rg in self.data.course_rg_compat[c]:
                    located[(sl, c, rg)] = self.add_var(f"located({sl},{c},{rg})")
        return located

    @timer
    def busy_vars_init(self):
        tutor_busy_slot = {}
        limit = 1000
        for i in self.data.instructors:
            other_dep_sched_courses = (
                self.data.other_departments_scheduled_courses_for_tutor[i]
                | self.data.other_departments_scheduled_courses_for_supp_tutor[i]
            )
            fixed_courses = self.data.fixed_courses_for_tutor[i]
            for sl in self.data.availability_slots:
                other_dep_sched_courses_for_sl = (
                    other_dep_sched_courses
                    & self.data.other_departments_sched_courses_for_avail_slot[sl]
                )
                other_dep_nb = len(other_dep_sched_courses_for_sl)
                fixed_courses_for_sl = (
                    fixed_courses & self.data.fixed_courses_for_avail_slot[sl]
                )
                fixed_courses_nb = len(fixed_courses_for_sl)
                tutor_busy_slot[(i, sl)] = self.add_var(f"tutor_busy_slot({i},{sl})")
                # Linking the variable to the scheduled dict
                expr = self.lin_expr()
                expr += limit * tutor_busy_slot[(i, sl)]
                for s_sl in slots_filter(self.data.courses_slots, simultaneous_to=sl):
                    for c in (
                        self.data.possible_courses[i]
                        & self.data.compatible_courses[s_sl]
                    ):
                        expr -= self.assigned[(s_sl, c, i)]
                # if assigned == 1 for some i, then IBS==1 !
                self.add_constraint(
                    expr,
                    ">=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.IBS_INF, instructors=i, slots=sl
                    ),
                )

                # If IBS == 1, then assigned equals 1 for
                # some OR (other_dep_nb + fixed_courses_nb)> 1
                self.add_constraint(
                    expr,
                    "<=",
                    (limit - 1) + other_dep_nb + fixed_courses_nb,
                    Constraint(
                        constraint_type=ConstraintType.IBS_SUP, instructors=i, slots=sl
                    ),
                )

                # if other_dep_nb + fixed_courses_nb > 1 for some i, then IBS==1 !
                self.add_constraint(
                    limit * tutor_busy_slot[(i, sl)],
                    ">=",
                    other_dep_nb + fixed_courses_nb,
                    Constraint(
                        constraint_type=ConstraintType.PROFESSEUR_A_DEJA_COURS_EN_AUTRE_DEPARTEMENT,
                        slots=sl,
                        instructors=i,
                    ),
                )

        tutor_busy_day = {}
        tutor_busy_halfday = {}
        for d in self.data.days:
            dayslots = slots_filter(self.data.availability_slots, day=d)
            for i in self.data.instructors:
                tutor_busy_day[(i, d)] = self.add_var()
                # Linking the variable to the scheduled dict
                card = 2 * len(dayslots)
                self.add_constraint(
                    card * tutor_busy_day[i, d]
                    - self.sum(tutor_busy_slot[i, sl] for sl in dayslots),
                    ">=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.IBD_INF, instructors=i, days=d
                    ),
                )
            for apm in self.data.possible_apms:
                halfdayslots = slots_filter(dayslots, apm=apm)
                for i in self.data.instructors:
                    tutor_busy_halfday[(i, d, apm)] = self.add_var()
                    # Linking the variable to the scheduled dict
                    card = 2 * len(halfdayslots)
                    expr = card * tutor_busy_halfday[i, d, apm] - self.sum(
                        tutor_busy_slot[i, sl] for sl in halfdayslots
                    )
                    self.add_constraint(
                        expr,
                        ">=",
                        0,
                        Constraint(
                            constraint_type=ConstraintType.IBHD_INF,
                            instructors=i,
                            days=d,
                        ),
                    )
                    self.add_constraint(
                        expr,
                        "<=",
                        card - 1,
                        Constraint(
                            constraint_type=ConstraintType.IBHD_SUP,
                            instructors=i,
                            days=d,
                        ),
                    )

        forced_tutor_busy_day = {}
        for i in self.data.instructors:
            for d in self.data.days:
                forced_tutor_busy_day[(i, d)] = 0
                if d in self.data.physical_presence_days_for_tutor[i]:
                    forced_tutor_busy_day[(i, d)] = 1
                if self.department.mode.cosmo == 1:
                    if self.data.sched_courses.filter(
                        start_time__date=d,
                        course__suspens=False,
                        course__tutor=i,
                    ).exists():
                        forced_tutor_busy_day[(i, d)] = 1
                self.add_constraint(
                    tutor_busy_day[i, d],
                    ">=",
                    forced_tutor_busy_day[(i, d)],
                    Constraint(
                        constraint_type=ConstraintType.FORCED_TBD, instructors=i, days=d
                    ),
                )

        tutor_busy_day_gte = {period: [] for period in self.periods}
        max_days = len(TimeGeneralSettings.objects.get(department=self.department).days)
        for period in self.periods:
            for j in range(max_days + 1):
                tutor_busy_day_gte[period].append({})

            for i in self.data.instructors:
                for j in range(1, max_days + 1):
                    tutor_busy_day_gte[period][j][i] = self.add_floor(
                        self.sum(
                            tutor_busy_day[(i, d)]
                            for d in days_filter(self.data.days, period=period)
                        ),
                        j,
                        max_days,
                    )
        group_busy_day = {}
        group_busy_halfday = {}
        for bg in self.data.basic_groups:
            for d in self.data.days:
                # add constraint linking GBD to EDT
                group_busy_day[(bg, d)] = self.add_var()
                dayslots = slots_filter(self.data.courses_slots, day=d)
                # Linking the variable to the scheduled dict
                card = 2 * len(dayslots)
                expr = card * group_busy_day[(bg, d)] - self.sum(
                    self.scheduled[(sl, c)]
                    for sl in dayslots
                    for c in self.data.all_courses_for_basic_group[bg]
                    & self.data.compatible_courses[sl]
                )
                self.add_constraint(
                    expr,
                    ">=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.GBD_INF, groups=bg, days=d
                    ),
                )
                self.add_constraint(
                    expr,
                    "<=",
                    card - 1,
                    Constraint(
                        constraint_type=ConstraintType.GBD_SUP, groups=bg, days=d
                    ),
                )

                for apm in self.possible_apms:
                    group_busy_halfday[(bg, d, apm)] = self.add_var(
                        f"GBHD({bg},{d},{apm})"
                    )
                    halfdayslots = slots_filter(dayslots, apm=apm)
                    card = 2 * len(halfdayslots)
                    expr = card * group_busy_halfday[(bg, d, apm)] - self.sum(
                        self.scheduled[(sl, c)]
                        for sl in halfdayslots
                        for c in self.data.all_courses_for_basic_group[bg]
                        & self.data.compatible_courses[sl]
                    )
                    self.add_constraint(
                        expr,
                        ">=",
                        0,
                        Constraint(
                            constraint_type=ConstraintType.GBHD_INF, groups=bg, days=d
                        ),
                    )
                    self.add_constraint(
                        expr,
                        "<=",
                        card - 1,
                        Constraint(
                            constraint_type=ConstraintType.GBHD_SUP, groups=bg, days=d
                        ),
                    )

        return (
            tutor_busy_day,
            tutor_busy_day_gte,
            tutor_busy_halfday,
            group_busy_day,
            group_busy_halfday,
            tutor_busy_slot,
            forced_tutor_busy_day,
        )

    @timer
    def visio_vars_init(self):
        physical_presence = {
            g: {
                (d, apm): self.add_var()
                for d in self.data.days
                for apm in [Time.AM, Time.PM]
            }
            for g in self.data.basic_groups
        }

        for g in self.data.basic_groups:
            for d, apm in physical_presence[g]:
                expr = 1000 * physical_presence[g][d, apm] - self.sum(
                    self.located[sl, c, r]
                    for c in self.data.all_courses_for_basic_group[g]
                    for r in self.data.course_rg_compat[c] - {None}
                    for sl in slots_filter(
                        self.data.compatible_slots[c], day=d, apm=apm
                    )
                )
                self.add_constraint(
                    expr,
                    "<=",
                    999,
                    Constraint(
                        constraint_type=ConstraintType.PHYSICAL_PRESENCE_SUP,
                        groups=g,
                        days=d,
                        apm=apm,
                    ),
                )
                self.add_constraint(
                    expr,
                    ">=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.PHYSICAL_PRESENCE_INF,
                        groups=g,
                        days=d,
                        apm=apm,
                    ),
                )

        has_visio = {
            g: {
                (d, apm): self.add_var()
                for d in self.data.days
                for apm in [Time.AM, Time.PM]
            }
            for g in self.data.basic_groups
        }

        for g in self.data.basic_groups:
            for d, apm in has_visio[g]:
                expr = 1000 * has_visio[g][d, apm] - self.sum(
                    self.located[sl, c, None]
                    for c in self.data.all_courses_for_basic_group[g]
                    for sl in slots_filter(
                        self.data.compatible_slots[c], day=d, apm=apm
                    )
                )
                self.add_constraint(
                    expr,
                    "<=",
                    999,
                    Constraint(
                        constraint_type=ConstraintType.HAS_VISIO,
                        groups=g,
                        days=d,
                        apm=apm,
                    ),
                )
                self.add_constraint(
                    expr,
                    ">=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.HAS_VISIO,
                        groups=g,
                        days=d,
                        apm=apm,
                    ),
                )

        return physical_presence, has_visio

    def add_to_slot_cost(self, slot, cost, period=None):
        self.slot_cost[slot] += cost

    def add_to_inst_cost(self, instructor, cost, period=None):
        self.tutor_cost[instructor][period] += cost

    def add_to_group_cost(self, group, cost, period=None):
        self.group_cost[group][period] += cost

    def add_to_generic_cost(self, cost, period=None):
        self.generic_cost[period] += cost

    @timer
    def add_stabilization_constraints(self):
        # maximize stability
        if self.major_to_stabilize is not None:
            st = StabilizeTutorsCourses.objects.create(
                department=self.department,
                version__major=self.major_to_stabilize,
                weight=MAX_WEIGHT,
            )
            sg = StabilizeGroupsCourses.objects.create(
                department=self.department,
                version__major=self.major_to_stabilize,
                weight=MAX_WEIGHT,
            )
            for period in self.periods:
                st.enrich_ttmodel(self, period, self.max_stab)
                sg.enrich_ttmodel(self, period, self.max_stab)
            print("Will stabilize from remote version #", self.major_to_stabilize)
            st.delete()
            sg.delete()

    @timer
    def add_core_constraints(self):
        """
        Add the core constraints to the PuLP model :
            - a course is scheduled once and only once
            - no group has two courses in parallel
            - + a teacher does not have 2 courses in parallel
              + the teachers are available on the chosen slots
            - no course on vacation days
        """
        # constraint : only one course per basic group on simultaneous slots
        # (and None if transversal ones)
        # Do not consider it if mode.cosmo == 2!
        if self.department.mode.cosmo != 2:
            if not NoSimultaneousGroupCourses.objects.filter(
                department=self.department
            ).exists():
                NoSimultaneousGroupCourses.objects.create(department=self.department)

        # a course is scheduled at most once
        for c in self.data.courses:
            self.add_constraint(
                self.sum(
                    [self.scheduled[(sl, c)] for sl in self.data.compatible_slots[c]]
                ),
                "<=",
                1,
                CourseConstraint(c),
            )

        # constraint : courses are scheduled only once
        if not ScheduleAllCourses.objects.filter(department=self.department).exists():
            ScheduleAllCourses.objects.create(department=self.department)

        # Check if RespectBound constraint is in database, and add it if not
        if not RespectTutorsMaxTimePerDay.objects.filter(
            department=self.department
        ).exists():
            RespectTutorsMaxTimePerDay.objects.create(department=self.department)

        # Check if RespectMinHours constraint is in database, and add it if not
        if not RespectTutorsMinTimePerDay.objects.filter(
            department=self.department
        ).exists():
            RespectTutorsMinTimePerDay.objects.create(department=self.department)

        # Check if MinimizeBusyDays constraint is in database, and add it if not
        if not MinimizeTutorsBusyDays.objects.filter(
            department=self.department
        ).exists():
            MinimizeTutorsBusyDays.objects.create(
                department=self.department, weight=MAX_WEIGHT
            )

        if not self.department.mode.cosmo:
            # Check if ConsiderPivots constraint is in database, and add it if not
            if not ConsiderPivots.objects.filter(department=self.department).exists():
                ConsiderPivots.objects.create(department=self.department)

            # Check if MinGroupsHalfDays constraint is in database, and add it if not
            if not MinGroupsHalfDays.objects.filter(
                department=self.department
            ).exists():
                MinGroupsHalfDays.objects.create(
                    department=self.department, weight=MAX_WEIGHT
                )

            # Check if ConsiderDependencies constraint is in database, and add it if not
            if not ConsiderDependencies.objects.filter(
                department=self.department
            ).exists():
                ConsiderDependencies.objects.create(department=self.department)

    @timer
    def add_instructors_constraints(self):
        # Each course is assigned to a unique tutor
        if not AssignAllCourses.objects.filter(department=self.department).exists():
            AssignAllCourses.objects.create(department=self.department)

        if not ConsiderTutorsUnavailability.objects.filter(
            department=self.department
        ).exists():
            ConsiderTutorsUnavailability.objects.create(department=self.department)

        if (
            not ConsiderModuleTutorRepartitions.objects.filter(
                department=self.department
            ).exists()
            and ModuleTutorRepartition.objects.filter(
                course_type__department=self.department
            ).exists()
        ):
            ConsiderModuleTutorRepartitions.objects.create(department=self.department)

        for i in self.data.instructors:
            if i.username == "---":
                continue
            for sl in self.data.availability_slots:
                if self.department.mode.visio:
                    # avail_at_school_instr consideration...
                    relevant_courses = set(
                        c
                        for c in self.data.possible_courses[i]
                        if None in self.data.course_rg_compat[c]
                    )
                    if self.pre_assign_rooms:
                        self.add_constraint(
                            self.sum(
                                self.assigned[(sl2, c2, i)]
                                - self.located[(sl2, c2, None)]
                                for sl2 in slots_filter(
                                    self.data.courses_slots, simultaneous_to=sl
                                )
                                for c2 in relevant_courses
                                & self.data.compatible_courses[sl2]
                            ),
                            "<=",
                            self.avail_at_school_instr[i][sl],
                            SlotInstructorConstraint(sl, i),
                        )

    @timer
    def add_rooms_constraints(self):
        # constraint : each Room is only used once on simultaneous slots
        if not LimitSimultaneousRoomCourses.objects.filter(
            department=self.department
        ).exists():
            LimitSimultaneousRoomCourses.objects.create(department=self.department)

        # each course is located into a room
        if not LocateAllCourses.objects.filter(department=self.department).exists():
            LocateAllCourses.objects.create(department=self.department)

        for sl in self.data.availability_slots:
            # constraint : fixed_courses rooms are not available
            for rg in self.data.rooms:
                fcrg = set(
                    fc
                    for fc in self.data.fixed_courses_for_avail_slot[sl]
                    if fc.room == rg
                )
                if fcrg:
                    for r in rg.basic_rooms():
                        self.add_constraint(
                            self.sum(
                                self.located[(s_sl, c, room)]
                                for s_sl in slots_filter(
                                    self.data.courses_slots, simultaneous_to=sl
                                )
                                for c in self.data.compatible_courses[s_sl]
                                for room in self.data.course_rg_compat[c] - {None}
                                if r in room.and_subrooms()
                            ),
                            "==",
                            0,
                            Constraint(
                                constraint_type=ConstraintType.CORE_ROOMS,
                                slots=sl,
                                rooms=r,
                            ),
                        )

    @timer
    def add_rooms_ponderations_constraints(self):
        considered_courses = set(self.data.courses)
        if self.department.mode.visio:
            considered_courses -= set(self.data.visio_courses)

        for rooms_ponderation in self.data.rooms_ponderations:
            room_types_id_list = rooms_ponderation.room_types
            room_types_list = [RoomType.objects.get(id=id) for id in room_types_id_list]
            ponderations = rooms_ponderation.ponderations
            n = len(ponderations)
            corresponding_basic_rooms = rooms_ponderation.basic_rooms.all()
            for sl in self.data.availability_slots:
                considered_basic_rooms = set(
                    b for b in corresponding_basic_rooms if self.avail_room[b][sl] != 0
                )
                bound = len(considered_basic_rooms)
                expr = self.lin_expr()
                for i in range(n):
                    ponderation = ponderations[i]
                    room_type = room_types_list[i]
                    expr += ponderation * self.sum(
                        self.scheduled[s_sl, c]
                        for s_sl in slots_filter(
                            self.data.courses_slots, simultaneous_to=sl
                        )
                        for c in self.data.courses_for_room_type[room_type]
                        & considered_courses
                        & self.data.compatible_courses[s_sl]
                    )
                self.add_constraint(
                    expr,
                    "<=",
                    bound,
                    Constraint(constraint_type=ConstraintType.ROOMTYPE_BOUND),
                )

    @timer
    def add_visio_room_constraints(self):
        # courses that are neither visio neither no-visio are preferentially not in Visio room
        for bg in self.data.basic_groups:
            group_courses_except_visio_and_no_visio_ones = (
                self.data.all_courses_for_basic_group[bg]
                - self.data.visio_courses
                - self.data.no_visio_courses
            )
            self.add_to_group_cost(
                bg,
                self.min_visio
                * self.sum(
                    self.located[(sl, c, None)] * self.data.visio_ponderation[c]
                    for c in group_courses_except_visio_and_no_visio_ones
                    for sl in self.data.compatible_slots[c]
                ),
            )

        # visio-courses are preferentially in Visio
        for bg in self.data.basic_groups:
            group_visio_courses = (
                self.data.all_courses_for_basic_group[bg] & self.data.visio_courses
            )
            self.add_to_group_cost(
                bg,
                self.min_visio
                * self.sum(
                    self.located[(sl, c, room)] * self.data.visio_ponderation[c]
                    for c in group_visio_courses
                    for room in self.data.course_rg_compat[c] - {None}
                    for sl in self.data.compatible_slots[c]
                ),
            )

        # No visio_course have (strongly) preferentially a room
        for bg in self.data.basic_groups:
            group_no_visio_courses = (
                self.data.all_courses_for_basic_group[bg] & self.data.no_visio_courses
            )
            self.add_to_group_cost(
                bg,
                10
                * self.min_visio
                * self.sum(
                    self.located[(sl, c, None)] * self.data.visio_ponderation[c]
                    for c in group_no_visio_courses
                    for sl in self.data.compatible_slots[c]
                ),
            )

    def send_unitary_lack_of_availability_mail(
        self, tutor, period, available_hours, teaching_hours, prefix="[flop!EDT] "
    ):
        subject = f"Manque de dispos période {period.name}"
        message = (
            "(Cet e-mail vous a été envoyé automatiquement par le générateur "
            "d'emplois du temps du logiciel flop!EDT)\n\n"
        )
        message += (
            f"Bonjour {tutor.first_name}\n"
            f"Semaine {period.name} vous ne donnez que {available_hours} heures de disponibilités, "
            f"alors que vous êtes censé⋅e assurer {teaching_hours} heures de cours...\n"
        )
        if self.data.holidays:
            message += f"(Notez qu'il y a {len(self.data.holidays)} jour(s) férié(s) cette semaine là...)\n"
        message += (
            f"Est-ce que vous avez la possibilité d'ajouter des créneaux de disponibilité ?\n"
            f"Sinon, pouvez-vous s'il vous plaît décaler des cours à une semaine précédente ou suivante ?\n"
            f"Merci d'avance.\n"
            f"Les gestionnaires d'emploi du temps."
        )

        message += (
            "\n\nPS: Attention, cet email risque de vous être renvoyé à chaque prochaine génération "
            "d'emploi du temps si vous n'avez pas fait les modifications attendues...\n"
            "N'hésitez pas à nous contacter en cas de souci."
        )
        email = EmailMessage(prefix + subject, message, to=(tutor.email,))
        email.send()

    def send_lack_of_availability_mail(self, prefix="[flop!EDT] "):
        for key in self.warnings:
            if key in self.data.instructors:
                for w in self.warnings[key]:
                    if " < " in w:
                        data = w.split(" ")
                        self.send_unitary_lack_of_availability_mail(
                            key, data[-1], data[0], data[4], prefix=prefix
                        )

    def compute_non_preferred_slots_cost(self):
        """
        Returns:
            - unp_slot_cost : a 2 level-dictionary
                            { teacher => availability_slot => cost (float in [0,1])}}
            - avail_instr : a 2 level-dictionary { teacher => availability_slot => 0/1 } including availability to home-teaching
            - avail_at_school_instr : idem, excluding home-teaching (usefull only in visio_mode)

        The slot cost will be:
            - 0 if it is a prefered slot
            - max(0., 2 - slot value / (average of slot values) )
        """

        avail_instr = {}
        avail_at_school_instr = {}
        unp_slot_cost = {}

        if self.data.holidays:
            self.add_warning(None, f"{self.data.holidays} are holidays")

        for i in self.data.instructors:
            avail_instr[i] = {}
            avail_at_school_instr[i] = {}
            unp_slot_cost[i] = {}
            for period in self.periods:
                period_availability_slots = slots_filter(
                    self.data.availability_slots, period=period
                )
                teaching_duration = sum(
                    [
                        c.duration
                        for c in self.data.courses_for_tutor[i]
                        if c.period == period
                    ],
                    dt.timedelta(),
                )
                total_teaching_duration = teaching_duration + sum(
                    [
                        c.duration
                        for c in self.data.other_departments_courses_for_tutor[i]
                        if c.period == period
                    ],
                    dt.timedelta(),
                )
                period_holidays = days_filter(self.data.holidays, period=period)

                if self.department.mode.cosmo != 1 and period_holidays:
                    period_tutor_availabilities = set(
                        a
                        for a in self.data.availabilities[i][period]
                        if a.date not in period_holidays
                    )
                else:
                    period_tutor_availabilities = self.data.availabilities[i][period]

                if not period_tutor_availabilities:
                    self.add_warning(
                        i, "no availability information given period %s" % period.name
                    )
                    for availability_slot in period_availability_slots:
                        unp_slot_cost[i][availability_slot] = 0
                        avail_at_school_instr[i][availability_slot] = 1
                        avail_instr[i][availability_slot] = 1

                else:
                    avail_time = sum(
                        [
                            a.duration
                            for a in period_tutor_availabilities
                            if a.value >= 1
                        ],
                        dt.timedelta(),
                    )

                    if avail_time < teaching_duration:
                        self.add_warning(
                            i,
                            "%g available hours < %g courses hours period %s"
                            % (
                                avail_time.seconds / 3600,
                                teaching_duration.seconds / 3600,
                                period.name,
                            ),
                        )
                        # We used to forget tutor availabilities in this case...
                        # for availability_slot in period_availability_slots:
                        #     unp_slot_cost[i][availability_slot] = 0
                        #     avail_at_school_instr[i][availability_slot] = 1
                        #     avail_instr[i][availability_slot] = 1

                    elif avail_time < total_teaching_duration:
                        self.add_warning(
                            i,
                            "%g available hours < %g courses hours including other deps period %s"
                            % (
                                avail_time.seconds / 3600,
                                total_teaching_duration.seconds / 3600,
                                period.name,
                            ),
                        )
                        # We used to forget tutor availabilities in this case...
                        # for availability_slot in period_availability_slots:
                        #     unp_slot_cost[i][availability_slot] = 0
                        #     avail_at_school_instr[i][availability_slot] = 1
                        #     avail_instr[i][availability_slot] = 1

                    elif (
                        avail_time < 2 * teaching_duration
                        and i.status == Tutor.FULL_STAFF
                    ):
                        self.add_warning(
                            i,
                            "only %g available hours for %g courses hours period %s"
                            % (
                                avail_time.seconds / 3600,
                                teaching_duration.seconds / 3600,
                                period.name,
                            ),
                        )
                    maximum = max(a.value for a in period_tutor_availabilities)
                    if maximum == 0:
                        for availability_slot in period_availability_slots:
                            unp_slot_cost[i][availability_slot] = 0
                            avail_at_school_instr[i][availability_slot] = 0
                            avail_instr[i][availability_slot] = 0
                        continue

                    non_prefered_duration_minutes = max(
                        1,
                        sum(
                            a.minutes
                            for a in period_tutor_availabilities
                            if 1 <= a.value <= maximum - 1
                        ),
                    )
                    average_value = (
                        sum(
                            a.minutes * a.value
                            for a in period_tutor_availabilities
                            if 1 <= a.value <= maximum - 1
                        )
                        / non_prefered_duration_minutes
                    )

                    for availability_slot in period_availability_slots:
                        avail = set(
                            a
                            for a in period_tutor_availabilities
                            if availability_slot.is_simultaneous_to(a)
                        )
                        if not avail:
                            print(
                                f"availability pbm for {i} availability_slot {availability_slot}"
                            )
                            unp_slot_cost[i][availability_slot] = 0
                            avail_at_school_instr[i][availability_slot] = 1
                            avail_instr[i][availability_slot] = 1
                            continue

                        minimum = min(a.value for a in avail)
                        if minimum == 0:
                            unp_slot_cost[i][availability_slot] = 0
                            avail_at_school_instr[i][availability_slot] = 0
                            avail_instr[i][availability_slot] = 0
                        elif minimum == 1:
                            unp_slot_cost[i][availability_slot] = 1
                            avail_at_school_instr[i][availability_slot] = 0
                            avail_instr[i][availability_slot] = 1
                        else:
                            avail_at_school_instr[i][availability_slot] = 1
                            avail_instr[i][availability_slot] = 1
                            value = minimum
                            if value == maximum:
                                unp_slot_cost[i][availability_slot] = 0
                            else:
                                unp_slot_cost[i][availability_slot] = (
                                    value - maximum
                                ) / (average_value - maximum)

            # Add fixed_courses constraint
            for sl in self.data.availability_slots:
                fixed_courses = (
                    self.data.fixed_courses_for_tutor[i]
                    & self.data.fixed_courses_for_avail_slot[sl]
                )

                if fixed_courses:
                    avail_instr[i][sl] = 0

        return avail_instr, avail_at_school_instr, unp_slot_cost

    def compute_non_preferred_slots_cost_course(self):
        """
        :returns
        non_preferred_cost_course :a 2 level dictionary
        { (CourseType, TrainingProgram)=> { Non-prefered availability_slot => cost (float in [0,1])}}

        avail_course : a 2 level-dictionary
        { (CourseType, TrainingProgram) => availability_slot => availability (0/1) }
        """

        non_preferred_cost_course = {}
        avail_course = {}
        for course_type in self.data.course_types:
            for promo in self.train_prog:
                avail_course[(course_type, promo)] = {}
                non_preferred_cost_course[(course_type, promo)] = {}
                for period in self.periods:
                    period_availability_slots = slots_filter(
                        self.data.availability_slots, period=period
                    )
                    courses_avail = set(
                        c_avail
                        for c_avail in self.data.courses_availabilities
                        if c_avail.course_type == course_type
                        and c_avail.train_prog == promo
                        and c_avail.date in period.dates()
                    )
                    if not courses_avail:
                        for availability_slot in period_availability_slots:
                            avail_course[(course_type, promo)][availability_slot] = 1
                            non_preferred_cost_course[(course_type, promo)][
                                availability_slot
                            ] = 0

                    else:
                        for availability_slot in period_availability_slots:
                            avail = set(
                                a
                                for a in courses_avail
                                if availability_slot.is_simultaneous_to(a)
                            )

                            if avail:
                                minimum = min(a.value for a in avail)
                                if minimum == 0:
                                    avail_course[(course_type, promo)][
                                        availability_slot
                                    ] = 0
                                    non_preferred_cost_course[(course_type, promo)][
                                        availability_slot
                                    ] = 100
                                else:
                                    avail_course[(course_type, promo)][
                                        availability_slot
                                    ] = 1
                                    value = minimum
                                    non_preferred_cost_course[(course_type, promo)][
                                        availability_slot
                                    ] = (1 - value / 8)

                            else:
                                avail_course[(course_type, promo)][
                                    availability_slot
                                ] = 1
                                non_preferred_cost_course[(course_type, promo)][
                                    availability_slot
                                ] = 0

        return non_preferred_cost_course, avail_course

    def compute_avail_room(self):
        avail_room = {}
        for room in self.data.basic_rooms:
            avail_room[room] = {}
            for sl in self.data.availability_slots:
                if RoomAvailability.objects.filter(
                    start_time__lt=sl.start_time + sl.duration,
                    start_time__gt=sl.start_time - F("duration"),
                    room=room,
                    value=0,
                ).exists():
                    avail_room[room][sl] = 0
                elif RoomReservation.objects.filter(
                    start_time__lt=sl.start_time + sl.duration,
                    end_time__gt=sl.start_time,
                    room=room,
                ).exists():
                    avail_room[room][sl] = 0
                else:
                    avail_room[room][sl] = 1

        return avail_room

    @timer
    def add_slot_preferences(self):
        """
        Add the constraints derived from the slot preferences expressed on the database
        """

        # first objective  => minimise use of unpreferred slots for teachers
        # ponderation MIN_UPS_I
        if not MinNonPreferedTutorsSlot.objects.filter(
            department=self.department
        ).exists():
            MinNonPreferedTutorsSlot.objects.create(
                weight=MAX_WEIGHT, department=self.department
            )

        # second objective  => minimise use of unpreferred slots for courses
        # ponderation MIN_UPS_C
        if not MinNonPreferedTrainProgsSlot.objects.filter(
            department=self.department
        ).exists():
            MinNonPreferedTrainProgsSlot.objects.create(
                weight=MAX_WEIGHT, department=self.department
            )

    @timer
    def add_other_departments_constraints(self):
        """
        Add the constraints imposed by other departments' scheduled courses.
        """

        for sl in self.data.availability_slots:
            # constraint : other_departments_sched_courses rooms are not available
            for r in self.data.basic_rooms:
                other_dep_sched_courses = (
                    self.data.other_departments_sched_courses_for_room[r]
                    & self.data.other_departments_sched_courses_for_avail_slot[sl]
                )
                if other_dep_sched_courses:
                    self.avail_room[r][sl] = 0

        for sl in self.data.availability_slots:
            # constraint : other_departments_sched_courses instructors are not available
            for i in self.data.instructors:
                other_dep_sched_courses = (
                    self.data.other_departments_scheduled_courses_for_tutor[i]
                    | self.data.other_departments_scheduled_courses_for_supp_tutor[i]
                ) & self.data.other_departments_sched_courses_for_avail_slot[sl]

                if other_dep_sched_courses:
                    self.avail_instr[i][sl] = 0

    def add_specific_constraints(self):
        """
        Add the active specific constraints stored in the database.
        """

        for period in self.periods:
            for constr in get_ttconstraints(
                self.department,
                period=period,
                is_active=True,
            ):
                if not self.core_only or constr.__class__ in [
                    AssignAllCourses,
                    ScheduleAllCourses,
                    NoSimultaneousGroupCourses,
                ]:
                    print(constr.__class__.__name__, constr.id, end=" - ")
                    timer(constr.enrich_ttmodel)(self, period)

        if self.pre_assign_rooms and not self.core_only:
            for period in self.periods:
                # Consider RoomConstraints that have enrich_ttmodel method
                for constr in get_room_constraints(
                    self.department, period=period, is_active=True
                ):
                    if hasattr(constr, "enrich_ttmodel"):
                        print(constr.__class__.__name__, constr.id, end=" - ")
                        timer(constr.enrich_ttmodel)(self, period)

    def update_objective(self):
        self.obj = self.lin_expr()
        for period in self.periods + [None]:
            for i in self.data.instructors:
                self.obj += self.tutor_cost[i][period]
            for g in self.data.basic_groups:
                self.obj += self.group_cost[g][period]
            self.obj += self.generic_cost[period]
        for sl in self.data.courses_slots:
            self.obj += self.slot_cost[sl]
        self.set_objective(self.obj)

    def add_aschedule_constraints(self):
        self.add_stabilization_constraints()

        self.add_core_constraints()

        # Has to be before add_rooms_constraints and add_instructors_constraints
        # because it contains rooms/instructors availability modification...
        self.add_other_departments_constraints()
        if self.pre_assign_rooms:
            if not self.department.mode.cosmo:
                self.add_rooms_constraints()
        else:
            self.add_rooms_ponderations_constraints()

        self.add_instructors_constraints()

        if self.pre_assign_rooms:
            if self.department.mode.visio:
                self.add_visio_room_constraints()

        self.add_slot_preferences()

        self.add_specific_constraints()

    def add_tt_to_db(self, target_major):
        close_old_connections()

        # remove target version
        ScheduledCourse.objects.filter(
            course__module__train_prog__department=self.department,
            course__period__in=self.periods,
            version__major=target_major,
        ).delete()

        # get or create TimetableVersions
        versions_dict = {}
        for period in self.periods:
            versions_dict[period] = TimetableVersion.objects.get_or_create(
                period=period, major=target_major, department=self.department
            )[0]
        if self.department.mode.cosmo == 2:
            corresponding_group = {}
            for i in self.data.instructors:
                corresponding_group[i] = self.data.groups.get(name=i.username)
            for c in self.data.courses:
                c.groups.clear()

        for c in self.data.courses:
            for sl in self.data.compatible_slots[c]:
                if self.get_var_value(self.scheduled[(sl, c)]) == 1:
                    cp = ScheduledCourse(
                        course=c,
                        start_time=sl.start_time,
                        version=versions_dict[c.period],
                    )
                    for i in self.data.possible_tutors[c]:
                        if self.get_var_value(self.assigned[(sl, c, i)]) == 1:
                            cp.tutor = i
                            if self.department.mode.cosmo == 2:
                                c.groups.add(corresponding_group[i])
                            break
                    if not self.department.mode.cosmo:
                        if self.pre_assign_rooms:
                            for rg in self.data.course_rg_compat[c]:
                                if self.get_var_value(self.located[(sl, c, rg)]) == 1:
                                    cp.room = rg
                                    break
                    cp.save()

        for fc in self.data.fixed_courses:
            cp = ScheduledCourse(
                course=fc.course,
                start_time=fc.start_time,
                day=fc.day,
                room=fc.room,
                version=versions_dict[fc.period],
                tutor=fc.tutor,
            )
            if ScheduledCourseAdditional.objects.filter(
                scheduled_course__id=fc.id
            ).exists():
                sca = fc.additional
                sca.pk = None
                sca.scheduled_course = cp
                sca.save()
            cp.save()

        # On imprime les différences si demandé
        if self.major_to_stabilize is not None:
            print_differences(
                self.department,
                self.periods,
                self.major_to_stabilize,
                target_major,
                self.data.instructors,
            )

        # # On enregistre les coûts dans la BDD
        TutorCost.objects.filter(
            department=self.department,
            period__in=self.data.periods,
            version__major=target_major,
        ).delete()
        GroupFreeHalfDay.objects.filter(
            group__train_prog__department=self.department,
            period__in=self.data.periods,
            version__major=target_major,
        ).delete()
        GroupCost.objects.filter(
            group__train_prog__department=self.department,
            period__in=self.data.periods,
            version__major=target_major,
        ).delete()

        for period in self.periods:
            for i in self.data.instructors:
                tc = TutorCost(
                    department=self.department,
                    tutor=i,
                    period=period,
                    value=self.get_expr_value(self.tutor_cost[i][period]),
                    version=versions_dict[period],
                )
                tc.save()

            for g in self.data.basic_groups:
                DJL = 0
                if Time.PM in self.possible_apms:
                    DJL += self.get_expr_value(
                        self.group_free_halfday[Time.PM][g][period]
                    )
                if Time.AM in self.possible_apms:
                    DJL += 0.01 * self.get_expr_value(
                        self.group_free_halfday[Time.AM][g][period]
                    )

                djlg = GroupFreeHalfDay(
                    group=g, period=period, version=versions_dict[period], DJL=DJL
                )
                djlg.save()
                cg = GroupCost(
                    group=g,
                    period=period,
                    version=versions_dict[period],
                    value=self.get_expr_value(self.group_cost[g][period]),
                )
                cg.save()

    # Some extra Utils
    def log_files_prefix(self):
        return f"TimetableModel_{self.department.abbrev}_{'_'.join(p.name for p in self.periods)}"

    def add_tt_to_db_from_file(self, filename=None, target_major=None):
        if filename is None:
            filename = self.last_counted_solution_filename()
        if target_major is None:
            target_major = self.choose_free_version_major()
        close_old_connections()
        # remove target working copy
        ScheduledCourse.objects.filter(
            course__module__train_prog__department=self.department,
            course__period__in=self.periods,
            version__major=target_major,
        ).delete()

        # get or create TimetableVersions
        versions_dict = {}
        for period in self.periods:
            versions_dict[period] = TimetableVersion.objects.get_or_create(
                period=period, major=target_major, department=self.department
            )[0]

        print("Added version #%g" % target_major)
        solution_file_one_vars_set = self.read_solution_file(filename)

        for c in self.data.courses:
            for sl in self.data.compatible_slots[c]:
                for i in self.data.possible_tutors[c]:
                    if (
                        self.assigned[(sl, c, i)].getName()
                        in solution_file_one_vars_set
                    ):
                        cp = ScheduledCourse(
                            course=c,
                            tutor=i,
                            start_time=sl.start_time,
                            day=sl.day.day,
                            version=versions_dict[c.period],
                        )
                        if self.pre_assign_rooms:
                            for rg in self.data.course_rg_compat[c]:
                                if (
                                    self.located[(sl, c, rg)].getName()
                                    in solution_file_one_vars_set
                                ):
                                    cp.room = rg
                                    break
                        cp.save()

        for fc in self.data.fixed_courses:
            cp = ScheduledCourse(
                course=fc.course,
                start_time=fc.start_time,
                day=fc.day,
                room=fc.room,
                version=versions_dict[fc.period],
                tutor=fc.tutor,
            )
            cp.save()

    def solve(
        self,
        time_limit=None,
        target_major=None,
        solver=GUROBI_NAME,
        threads=None,
        ignore_sigint=True,
        send_gurobi_logs_email_to=None,
        with_numerotation=True,
    ):
        """
        Generates a schedule from the TimetableModel
        The solver stops either when the best schedule is obtained or timeLimit
        is reached.

        If major_to_stabilize is None: does not move the scheduled courses
        whose group is not in train_prog and fetches from the remote database
        these scheduled courses with version number 0.

        If target_major is given, stores the resulting schedule under this
        version number.
        If target_major is not given, stores under the lowest version
        number that is greater than the maximum version numbers for the
        considered period.
        Returns the version
        """
        print(f"\nLet's solve periods {[p.name for p in self.periods]}")

        self.update_objective()

        result = self.optimize(
            time_limit, solver, threads=threads, ignore_sigint=ignore_sigint
        )

        if result is not None:
            if target_major is None:
                if self.department.mode.cosmo == 2:
                    target_major = 0
                else:
                    target_major = self.choose_free_version_major()

            self.add_tt_to_db(target_major)
            print(f"Added work copy N°{target_major}")
            if self.post_assign_rooms:
                RoomModel(self.department.abbrev, self.periods, target_major).solve()
                print("Rooms assigned")
            if with_numerotation:
                number_courses(
                    self.department, periods=self.periods, version_major=target_major
                )

        if send_gurobi_logs_email_to is not None:
            if result is None:
                solved = False
                subject = f"Logs {self.department.abbrev} {self.periods} : not solved"
            else:
                solved = True
                subject = f"Logs {self.department.abbrev} {self.periods} : copy {target_major}"
            self.send_gurobi_log_files_email(
                subject=subject, to=[send_gurobi_logs_email_to], solved=solved
            )

        return target_major

    def find_same_course_slot_in_other_period(self, slot, other_period):
        other_slots = slots_filter(
            self.data.courses_slots, period=other_period, same=slot
        )
        if len(other_slots) != 1:
            raise Exception(
                f"Wrong slots among periods {other_period} \n {slot} vs {other_slots}"
            )
        return other_slots.pop()

    def send_gurobi_log_files_email(self, subject, to, solved):

        message = gettext(
            "This email was automatically sent by the flop!EDT timetable generator\n\n"
        )
        if solved:
            message += gettext("Here is the log of the last run of the generator:\n\n")
            logs = open(self.gurobi_log_file(), "r").read().split("logging started")
            if self.post_assign_rooms:
                message += logs[-2] + "\n\n"
                message += logs[-1] + "\n\n"
            else:
                message += logs[-1] + "\n\n"
        else:
            message += (
                open(
                    "%s/constraints_summary%s.txt"
                    % (iis_files_path, self.iis_filename_suffixe()),
                    mode="r",
                    encoding="utf-8",
                    errors="replace",
                ).read()
                + "\n\n"
            )
            message += open(
                "%s/constraints_factorised%s.txt"
                % (iis_files_path, self.iis_filename_suffixe()),
                mode="r",
                encoding="utf-8",
                errors="replace",
            ).read()

        email = EmailMessage(subject, message, to=to)
        email.send()
