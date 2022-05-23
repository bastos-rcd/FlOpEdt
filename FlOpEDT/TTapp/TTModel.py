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

from base.models import RoomType, RoomPreference, ScheduledCourse, TrainingProgramme, \
    TutorCost, GroupFreeHalfDay, GroupCost, TimeGeneralSettings, ModuleTutorRepartition, ScheduledCourseAdditional

from base.timing import Time

from people.models import Tutor

from TTapp.models import MinNonPreferedTutorsSlot, StabilizeTutorsCourses, MinNonPreferedTrainProgsSlot, \
    NoSimultaneousGroupCourses, ScheduleAllCourses, AssignAllCourses, ConsiderTutorsUnavailability, \
    MinimizeBusyDays, MinGroupsHalfDays, RespectMaxHoursPerDay, ConsiderDependencies, ConsiderPivots, \
    StabilizeGroupsCourses, RespectMinHoursPerDay

from TTapp.FlopConstraint import max_weight

from TTapp.slots import slots_filter, days_filter

from TTapp.WeeksDatabase import WeeksDatabase


from django.db import close_old_connections
from django.db.models import F

from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraints.courseConstraint import CourseConstraint

from TTapp.ilp_constraints.constraints.slotInstructorConstraint import SlotInstructorConstraint

from core.decorators import timer

from TTapp.FlopModel import FlopModel, GUROBI_NAME, get_ttconstraints, get_room_constraints
from TTapp.RoomModel import RoomModel

from django.utils.translation import gettext_lazy as _


class TTModel(FlopModel):
    @timer
    def __init__(self, department_abbrev, weeks,
                 train_prog=None,
                 stabilize_work_copy=None,
                 min_nps_i=1.,
                 min_bhd_g=1.,
                 min_bd_i=1.,
                 min_bhd_i=1.,
                 min_nps_c=1.,
                 max_stab=5.,
                 lim_ld=1.,
                 core_only=False,
                 send_mails=False,
                 slots_step=None,
                 keep_many_solution_files=False,
                 min_visio=0.5,
                 pre_assign_rooms=False,
                 post_assign_rooms=True):
        # beg_file = os.path.join('logs',"FlOpTT")
        super(TTModel, self).__init__(department_abbrev, weeks, keep_many_solution_files=keep_many_solution_files)
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
        print(_(f"\nLet's start weeks #{self.weeks}"))
        assignment_text = ""
        if self.pre_assign_rooms:
            assignment_text += 'pre'
            if self.post_assign_rooms:
                assignment_text += ' & post'
        elif self.post_assign_rooms:
            assignment_text += 'post'
        else:
            assignment_text += 'no'
        print(_("Rooms assignment :"), assignment_text)



        if train_prog is None:
            train_prog = TrainingProgramme.objects.filter(department=self.department)
        else:
            try:
                iter(train_prog)
            except TypeError:
                train_prog = TrainingProgramme.objects.filter(id=train_prog.id)
            print(_(f'Will modify only courses of training programme(s) {train_prog}'))
        self.train_prog = train_prog
        self.stabilize_work_copy = stabilize_work_copy
        self.wdb = self.wdb_init()
        self.courses = self.wdb.courses
        if not self.wdb.courses.exists():
            print('There are no course to be scheduled...')
            return
        self.possible_apms = self.wdb.possible_apms
        self.cost_I, self.FHD_G, self.cost_G, self.cost_SL, self.generic_cost = self.costs_init()
        self.TT, self.TTinstructors = self.TT_vars_init()
        if self.pre_assign_rooms:
            self.TTrooms = self.TTrooms_init()
        self.IBD, self.IBD_GTE, self.IBHD, self.GBHD, self.IBS, self.forced_IBD = self.busy_vars_init()
        if self.pre_assign_rooms:
            if self.department.mode.visio:
                self.physical_presence, self.has_visio = self.visio_vars_init()
        self.avail_instr, self.avail_at_school_instr, self.unp_slot_cost \
            = self.compute_non_preferred_slots_cost()
        self.unp_slot_cost_course, self.avail_course \
            = self.compute_non_preferred_slots_cost_course()
        self.avail_room = self.compute_avail_room()

        # Hack : permet que ça marche même si les dispos sur la base sont pas complètes
        for i in self.wdb.instructors:
            for availability_slot in self.wdb.availability_slots:
                if availability_slot not in self.avail_instr[i]:
                    self.avail_instr[i][availability_slot] = 0
                if availability_slot not in self.unp_slot_cost[i]:
                    self.unp_slot_cost[i][availability_slot] = 0

        self.add_TT_constraints()

        if self.warnings:
            print(_("Relevant warnings :"))
            for key, key_warnings in self.warnings.items():
                print("%s : %s" % (key, ", ".join([str(x) for x in key_warnings])))

        if self.send_mails:
            self.send_lack_of_availability_mail()

    @timer
    def wdb_init(self):
        wdb = WeeksDatabase(self.department, self.weeks, self.train_prog, self.slots_step)
        return wdb

    @timer
    def costs_init(self):
        cost_I = dict(list(zip(self.wdb.instructors,
                               [{week: self.lin_expr() for week in self.weeks + [None]} for _ in
                                self.wdb.instructors])))
        FHD_G = {}
        for apm in self.possible_apms:
            FHD_G[apm] = dict(
                list(zip(self.wdb.basic_groups,
                         [{week: self.lin_expr() for week in self.weeks} for _ in self.wdb.basic_groups])))

        cost_G = dict(
            list(zip(self.wdb.basic_groups,
                     [{week: self.lin_expr() for week in self.weeks + [None]} for _ in self.wdb.basic_groups])))

        cost_SL = dict(
            list(zip(self.wdb.courses_slots,
                     [self.lin_expr() for _ in self.wdb.courses_slots])))

        generic_cost = {week: self.lin_expr() for week in self.weeks + [None]}

        return cost_I, FHD_G, cost_G, cost_SL, generic_cost

    @timer
    def TT_vars_init(self):
        TT = {}
        TTinstructors = {}

        for sl in self.wdb.courses_slots:
            for c in self.wdb.compatible_courses[sl]:
                TT[(sl, c)] = self.add_var("TT(%s,%s)" % (sl, c))
                for i in self.wdb.possible_tutors[c]:
                    TTinstructors[(sl, c, i)] \
                        = self.add_var("TTinstr(%s,%s,%s)" % (sl, c, i))
        return TT, TTinstructors

    @timer
    def TTrooms_init(self):
        TTrooms = {}
        for sl in self.wdb.courses_slots:
            for c in self.wdb.compatible_courses[sl]:
                for rg in self.wdb.course_rg_compat[c]:
                    TTrooms[(sl, c, rg)] \
                        = self.add_var("TTroom(%s,%s,%s)" % (sl, c, rg))
        return TTrooms

    @timer
    def busy_vars_init(self):
        IBS = {}
        limit = 1000
        for i in self.wdb.instructors:
            other_dep_sched_courses = self.wdb.other_departments_scheduled_courses_for_tutor[i] \
                                      | self.wdb.other_departments_scheduled_courses_for_supp_tutor[i]
            fixed_courses = self.wdb.fixed_courses_for_tutor[i]
            for sl in self.wdb.availability_slots:
                other_dep_sched_courses_for_sl = other_dep_sched_courses \
                                                 & self.wdb.other_departments_sched_courses_for_avail_slot[sl]
                other_dep_nb = len(other_dep_sched_courses_for_sl)
                fixed_courses_for_sl = fixed_courses & self.wdb.fixed_courses_for_avail_slot[sl]
                fixed_courses_nb = len(fixed_courses_for_sl)
                IBS[(i, sl)] = self.add_var("IBS(%s,%s)" % (i, sl))
                # Linking the variable to the TT
                expr = self.lin_expr()
                expr += limit * IBS[(i, sl)]
                for s_sl in slots_filter(self.wdb.courses_slots, simultaneous_to=sl):
                    for c in self.wdb.possible_courses[i] & self.wdb.compatible_courses[s_sl]:
                        expr -= self.TTinstructors[(s_sl, c, i)]
                # if TTinstructors == 1 for some i, then IBS==1 !
                self.add_constraint(expr, '>=', 0,
                                    Constraint(constraint_type=ConstraintType.IBS_INF, instructors=i, slots=sl))

                # If IBS == 1, then TTinstructors equals 1 for some OR (other_dep_nb + fixed_courses_nb)> 1
                self.add_constraint(expr, '<=', (limit - 1) + other_dep_nb + fixed_courses_nb,
                                    Constraint(constraint_type=ConstraintType.IBS_SUP, instructors=i, slots=sl))

                # if other_dep_nb + fixed_courses_nb > 1 for some i, then IBS==1 !
                self.add_constraint(limit * IBS[(i, sl)], '>=', other_dep_nb + fixed_courses_nb,
                                    Constraint(constraint_type=
                                               ConstraintType.PROFESSEUR_A_DEJA_COURS_EN_AUTRE_DEPARTEMENT,
                                               slots=sl, instructors=i))

        IBD = {}
        IBHD = {}
        for d in self.wdb.days:
            dayslots = slots_filter(self.wdb.availability_slots, day=d)
            for i in self.wdb.instructors:
                IBD[(i, d)] = self.add_var()
                # Linking the variable to the TT
                card = 2 * len(dayslots)
                self.add_constraint(card * IBD[i, d] - self.sum(IBS[i, sl] for sl in dayslots), '>=', 0,
                                    Constraint(constraint_type=ConstraintType.IBD_INF, instructors=i, days=d))
            for apm in self.wdb.possible_apms:
                halfdayslots = slots_filter(dayslots, apm=apm)
                for i in self.wdb.instructors:
                    IBHD[(i, d, apm)] = self.add_var()
                    # Linking the variable to the TT
                    card = 2 * len(halfdayslots)
                    self.add_constraint(card * IBHD[i, d, apm] - self.sum(IBS[i, sl] for sl in halfdayslots), '>=',
                                        0,
                                        Constraint(constraint_type=ConstraintType.IBHD_INF, instructors=i, days=d))

        forced_IBD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                forced_IBD[(i, d)] = 0
                if d.day in self.wdb.physical_presence_days_for_tutor[i][d.week]:
                    forced_IBD[(i, d)] = 1
                if self.department.mode.cosmo == 1:
                    if self.wdb.sched_courses.filter(day=d.day, course__week=d.week,
                                                     course__suspens=False,
                                                     course__tutor=i).exists():
                        forced_IBD[(i, d)] = 1
                self.add_constraint(IBD[i, d], '>=', forced_IBD[(i, d)],
                                    Constraint(constraint_type=ConstraintType.forced_IBD, instructors=i, days=d))

        IBD_GTE = {week: [] for week in self.weeks}
        max_days = len(TimeGeneralSettings.objects.get(department=self.department).days)
        for week in self.weeks:
            for j in range(max_days + 1):
                IBD_GTE[week].append({})

            for i in self.wdb.instructors:
                for j in range(1, max_days + 1):
                    IBD_GTE[week][j][i] = self.add_floor(self.sum(IBD[(i, d)]
                                                                  for d in days_filter(self.wdb.days, week=week)),
                                                         j,
                                                         max_days)

        GBHD = {}
        for bg in self.wdb.basic_groups:
            for d in self.wdb.days:
                # add constraint linking IBD to EDT
                for apm in self.possible_apms:
                    GBHD[(bg, d, apm)] \
                        = self.add_var("GBHD(%s,%s,%s)" % (bg, d, apm))
                    halfdayslots = slots_filter(self.wdb.courses_slots, day=d, apm=apm)
                    card = 2 * len(halfdayslots)
                    expr = self.lin_expr()
                    expr += card * GBHD[(bg, d, apm)]
                    for sl in halfdayslots:
                        for c in self.wdb.all_courses_for_basic_group[bg] & self.wdb.compatible_courses[sl]:
                            expr -= self.TT[(sl, c)]
                    self.add_constraint(expr, '>=', 0,
                                        Constraint(constraint_type=ConstraintType.GBHD_INF, groups=bg, days=d))
                    self.add_constraint(expr, '<=', card - 1,
                                        Constraint(constraint_type=ConstraintType.GBHD_SUP, groups=bg, days=d))

        return IBD, IBD_GTE, IBHD, GBHD, IBS, forced_IBD

    @timer
    def visio_vars_init(self):
        physical_presence = {g: {(d, apm): self.add_var()
                                for d in self.wdb.days for apm in [Time.AM, Time.PM]}
                             for g in self.wdb.basic_groups}

        for g in self.wdb.basic_groups:
            for (d, apm) in physical_presence[g]:
                expr = 1000 * physical_presence[g][d, apm] \
                       - self.sum(self.TTrooms[sl, c, r]
                                  for c in self.wdb.all_courses_for_basic_group[g]
                                  for r in self.wdb.course_rg_compat[c] - {None}
                                  for sl in slots_filter(self.wdb.compatible_slots[c], day=d, apm=apm))
                self.add_constraint(expr, '<=', 999,
                                    Constraint(constraint_type=ConstraintType.PHYSICAL_PRESENCE_SUP, groups=g,
                                               days=d, apm=apm))
                self.add_constraint(expr, '>=', 0,
                                    Constraint(constraint_type=ConstraintType.PHYSICAL_PRESENCE_INF, groups=g,
                                               days=d, apm=apm))

        has_visio = {g: {(d, apm): self.add_var()
                         for d in self.wdb.days for apm in [Time.AM, Time.PM]}
                     for g in self.wdb.basic_groups}

        for g in self.wdb.basic_groups:
            for (d, apm) in has_visio[g]:
                expr = 1000 * has_visio[g][d, apm] \
                       - self.sum(self.TTrooms[sl, c, None]
                                  for c in self.wdb.all_courses_for_basic_group[g]
                                  for sl in slots_filter(self.wdb.compatible_slots[c], day=d, apm=apm))
                self.add_constraint(expr, '<=', 999,
                                    Constraint(constraint_type=ConstraintType.HAS_VISIO, groups=g, days=d, apm=apm))
                self.add_constraint(expr, '>=', 0,
                                    Constraint(constraint_type=ConstraintType.HAS_VISIO, groups=g, days=d, apm=apm))

        return physical_presence, has_visio

    def add_to_slot_cost(self, slot, cost):
        self.cost_SL[slot] += cost

    def add_to_inst_cost(self, instructor, cost, week=None):
        self.cost_I[instructor][week] += cost

    def add_to_group_cost(self, group, cost, week=None):
        self.cost_G[group][week] += cost

    def add_to_generic_cost(self, cost, week=None):
        self.generic_cost[week] += cost

    @timer
    def add_stabilization_constraints(self):
        # maximize stability
        if self.stabilize_work_copy is not None:
            st = StabilizeTutorsCourses.objects.create(department=self.department,
                                                       work_copy=self.stabilize_work_copy, weight=max_weight)
            sg = StabilizeGroupsCourses.objects.create(department=self.department,
                                                       work_copy=self.stabilize_work_copy, weight=max_weight)
            for week in self.weeks:
                st.enrich_ttmodel(self, week, self.max_stab)
                sg.enrich_ttmodel(self, week, self.max_stab)
            print('Will stabilize from remote work copy #', \
                  self.stabilize_work_copy)
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
            if not NoSimultaneousGroupCourses.objects.filter(department=self.department).exists():
                NoSimultaneousGroupCourses.objects.create(department=self.department)

        # a course is scheduled at most once
        for c in self.wdb.courses:
            self.add_constraint(self.sum([self.TT[(sl, c)] for sl in self.wdb.compatible_slots[c]]),
                                '<=', 1,
                                CourseConstraint(c))

        # constraint : courses are scheduled only once
        if not ScheduleAllCourses.objects.filter(department=self.department).exists():
            ScheduleAllCourses.objects.create(department=self.department)

        # Check if RespectBound constraint is in database, and add it if not
        if not RespectMaxHoursPerDay.objects.filter(department=self.department).exists():
            RespectMaxHoursPerDay.objects.create(department=self.department)

        # Check if RespectMinHours constraint is in database, and add it if not
        if not RespectMinHoursPerDay.objects.filter(department=self.department).exists():
            RespectMinHoursPerDay.objects.create(department=self.department)

        # Check if MinimizeBusyDays constraint is in database, and add it if not
        if not MinimizeBusyDays.objects.filter(department=self.department).exists():
            MinimizeBusyDays.objects.create(department=self.department, weight=max_weight)

        if not self.department.mode.cosmo:
            # Check if ConsiderPivots constraint is in database, and add it if not
            if not ConsiderPivots.objects.filter(department=self.department).exists():
                ConsiderPivots.objects.create(department=self.department)

            # Check if MinGroupsHalfDays constraint is in database, and add it if not
            if not MinGroupsHalfDays.objects.filter(department=self.department).exists():
                MinGroupsHalfDays.objects.create(department=self.department, weight=max_weight)
    
            # Check if ConsiderDependencies constraint is in database, and add it if not
            if not ConsiderDependencies.objects.filter(department=self.department).exists():
                ConsiderDependencies.objects.create(department=self.department)

    @timer
    def add_instructors_constraints(self):
        # Each course is assigned to a unique tutor
        if not AssignAllCourses.objects.filter(department=self.department).exists():
            AssignAllCourses.objects.create(department=self.department)

        if not ConsiderTutorsUnavailability.objects.filter(department=self.department).exists():
            ConsiderTutorsUnavailability.objects.create(department=self.department)

        for i in self.wdb.instructors:
            if i.username == '---':
                continue
            for sl in self.wdb.availability_slots:
                if self.department.mode.visio:
                    # avail_at_school_instr consideration...
                    relevant_courses = set(c for c in self.wdb.possible_courses[i]
                                           if None in self.wdb.course_rg_compat[c])
                    if self.pre_assign_rooms:
                        self.add_constraint(
                            self.sum(self.TTinstructors[(sl2, c2, i)] - self.TTrooms[(sl2, c2, None)]
                                     for sl2 in slots_filter(self.wdb.courses_slots, simultaneous_to=sl)
                                     for c2 in relevant_courses & self.wdb.compatible_courses[sl2]),
                            '<=', self.avail_at_school_instr[i][sl],
                            SlotInstructorConstraint(sl, i)
                        )

        for mtr in ModuleTutorRepartition.objects.filter(module__in=self.wdb.modules,
                                                         week__in=self.weeks):
            self.add_constraint(
                self.sum(self.TTinstructors[sl, c, mtr.tutor]
                         for c in set(c for c in self.wdb.courses if c.module == mtr.module
                                      and c.type == mtr.course_type and c.tutor is None)
                         for sl in slots_filter(self.wdb.compatible_slots[c],
                                                week=mtr.week)
                         ),
                '==', mtr.courses_nb, Constraint(constraint_type=ConstraintType.MODULETUTORREPARTITION)
            )

    @timer
    def add_rooms_constraints(self):
        # constraint : each Room is only used once on simultaneous slots
        for r in self.wdb.basic_rooms:
            for sl in self.wdb.availability_slots:
                self.add_constraint(self.sum(self.TTrooms[(sl2, c, rg)]
                                             for (c, rg) in self.wdb.room_course_compat[r]
                                             for sl2 in slots_filter(self.wdb.compatible_slots[c], simultaneous_to=sl)
                                             ),
                                    '<=', self.avail_room[r][sl],
                                    Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                               rooms=r, slots=sl))

        for sl in self.wdb.courses_slots:
            # constraint : each course is assigned to a Room
            for c in self.wdb.compatible_courses[sl]:
                self.add_constraint(
                    self.sum(self.TTrooms[(sl, c, r)] for r in self.wdb.course_rg_compat[c]) - self.TT[(sl, c)],
                    '==', 0,
                    Constraint(constraint_type=ConstraintType.CORE_ROOMS, slots=sl, courses=c))

        for sl in self.wdb.availability_slots:
            # constraint : fixed_courses rooms are not available
            for rg in self.wdb.rooms:
                fcrg = set(fc for fc in self.wdb.fixed_courses_for_avail_slot[sl] if fc.room == rg)
                # if self.wdb.fixed_courses.filter((Q(start_time__lt=sl.start_time + sl.duration) |
                #                                   Q(start_time__gt=sl.start_time - F('course__type__duration'))),
                #                                  room=rg, day=sl.day).exists():
                if fcrg:
                    for r in rg.basic_rooms():
                        self.add_constraint(self.sum(self.TTrooms[(s_sl, c, room)]
                                                     for s_sl in slots_filter(self.wdb.courses_slots, simultaneous_to=sl)
                                                     for c in self.wdb.compatible_courses[s_sl]
                                                     for room in self.wdb.course_rg_compat[c] - {None}
                                                     if r in room.and_subrooms()),
                                            '==', 0,
                                            Constraint(constraint_type=ConstraintType.CORE_ROOMS,
                                                       slots=sl, rooms=r))

    @timer
    def add_rooms_ponderations_constraints(self):
        considered_courses = set(self.wdb.courses)
        if self.department.mode.visio:
            considered_courses -= set(self.wdb.visio_courses)

        for rooms_ponderation in self.wdb.rooms_ponderations:
            room_types_id_list = rooms_ponderation.room_types
            room_types_list = [RoomType.objects.get(id=id) for id in room_types_id_list]
            ponderations = rooms_ponderation.ponderations
            n = len(ponderations)
            corresponding_basic_rooms = rooms_ponderation.basic_rooms.all()
            for sl in self.wdb.availability_slots:
                considered_basic_rooms = set(b for b in corresponding_basic_rooms
                                             if self.avail_room[b][sl] != 0)
                bound = len(considered_basic_rooms)
                expr = self.lin_expr()
                for i in range(n):
                    ponderation = ponderations[i]
                    room_type = room_types_list[i]
                    expr += ponderation * self.sum(self.TT[s_sl, c]
                                                   for s_sl in slots_filter(self.wdb.courses_slots, simultaneous_to=sl)
                                                   for c in self.wdb.courses_for_room_type[room_type]
                                                   & considered_courses
                                                   & self.wdb.compatible_courses[s_sl]
                                                   )
                self.add_constraint(
                    expr, '<=', bound, Constraint(constraint_type=ConstraintType.ROOMTYPE_BOUND)
                )

    @timer
    def add_visio_room_constraints(self):
        # courses that are neither visio neither no-visio are preferentially not in Visio room
        for bg in self.wdb.basic_groups:
            group_courses_except_visio_and_no_visio_ones = \
                self.wdb.all_courses_for_basic_group[bg] - self.wdb.visio_courses - self.wdb.no_visio_courses
            self.add_to_group_cost(bg,
                                   self.min_visio *
                                   self.sum(self.TTrooms[(sl, c, None)] * self.wdb.visio_ponderation[c]
                                            for c in group_courses_except_visio_and_no_visio_ones
                                            for sl in self.wdb.compatible_slots[c])
                                   )

        # visio-courses are preferentially in Visio
        for bg in self.wdb.basic_groups:
            group_visio_courses= \
                self.wdb.all_courses_for_basic_group[bg] & self.wdb.visio_courses
            self.add_to_group_cost(bg,
                                   self.min_visio *
                                   self.sum(self.TTrooms[(sl, c, room)] * self.wdb.visio_ponderation[c]
                                            for c in group_visio_courses
                                            for room in self.wdb.course_rg_compat[c] - {None}
                                            for sl in self.wdb.compatible_slots[c])
                                   )

        # No visio_course have (strongly) preferentially a room
        for bg in self.wdb.basic_groups:
            group_no_visio_courses = self.wdb.all_courses_for_basic_group[bg] & self.wdb.no_visio_courses
            self.add_to_group_cost(bg,
                                   10 * self.min_visio *
                                   self.sum(self.TTrooms[(sl, c, None)] * self.wdb.visio_ponderation[c]
                                            for c in group_no_visio_courses
                                            for sl in self.wdb.compatible_slots[c])
                                   )


    def send_unitary_lack_of_availability_mail(self, tutor, week, available_hours, teaching_hours,
                                               prefix="[flop!EDT] "):
        subject = f"Manque de dispos semaine {week}"
        message = "(Cet e-mail vous a été envoyé automatiquement par le générateur " \
                  "d'emplois du temps du logiciel flop!EDT)\n\n"
        message += f"Bonjour {tutor.first_name}\n" \
                   f"Semaine {week} vous ne donnez que {available_hours} heures de disponibilités, " \
                   f"alors que vous êtes censé⋅e assurer {teaching_hours} heures de cours...\n"
        if self.wdb.holidays:
            message += f"(Notez qu'il y a {len(self.wdb.holidays)} jour(s) férié(s) cette semaine là...)\n"
        message += f"Est-ce que vous avez la possibilité d'ajouter des créneaux de disponibilité ?\n" \
                   f"Sinon, pouvez-vous s'il vous plaît décaler des cours à une semaine précédente ou suivante ?\n" \
                   f"Merci d'avance.\n" \
                   f"Les gestionnaires d'emploi du temps."

        message += "\n\nPS: Attention, cet email risque de vous être renvoyé à chaque prochaine génération " \
                   "d'emploi du temps si vous n'avez pas fait les modifications attendues...\n" \
                   "N'hésitez pas à nous contacter en cas de souci."
        email = EmailMessage(
            prefix + subject,
            message,
            to=(tutor.email,)
        )
        email.send()

    def send_lack_of_availability_mail(self, prefix="[flop!EDT] "):
        for key in self.warnings:
            if key in self.wdb.instructors:
                for w in self.warnings[key]:
                    if ' < ' in w:
                        data = w.split(' ')
                        self.send_unitary_lack_of_availability_mail(key, data[-1], data[0], data[4],
                                                                    prefix=prefix)

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

        if self.wdb.holidays:
            self.add_warning(None, "%s are holidays" % self.wdb.holidays)

        for i in self.wdb.instructors:
            avail_instr[i] = {}
            avail_at_school_instr[i] = {}
            unp_slot_cost[i] = {}
            for week in self.weeks:
                week_availability_slots = slots_filter(self.wdb.availability_slots, week=week)
                teaching_duration = sum(c.type.duration
                                        for c in self.wdb.courses_for_tutor[i] if c.week == week)
                total_teaching_duration = teaching_duration + sum(c.type.duration
                                                                  for c in
                                                                  self.wdb.other_departments_courses_for_tutor[i]
                                                                  if c.week == week)
                week_holidays = [d.day for d in days_filter(self.wdb.holidays, week=week)]
                if self.department.mode.cosmo != 1 and week_holidays:
                    week_tutor_availabilities = set(
                        a for a in self.wdb.availabilities[i][week]
                        if a.day not in week_holidays)
                else:
                    week_tutor_availabilities = self.wdb.availabilities[i][week]

                if not week_tutor_availabilities:
                    self.add_warning(i, "no availability information given week %s" % week)
                    for availability_slot in week_availability_slots:
                        unp_slot_cost[i][availability_slot] = 0
                        avail_at_school_instr[i][availability_slot] = 1
                        avail_instr[i][availability_slot] = 1

                else:
                    avail_time = sum(a.duration for a in week_tutor_availabilities if a.value >= 1)

                    if avail_time < teaching_duration:
                        self.add_warning(i, "%g available hours < %g courses hours week %s" %
                                         (avail_time / 60, teaching_duration / 60, week))
                        # We used to forget tutor availabilities in this case...
                        # for availability_slot in week_availability_slots:
                        #     unp_slot_cost[i][availability_slot] = 0
                        #     avail_at_school_instr[i][availability_slot] = 1
                        #     avail_instr[i][availability_slot] = 1

                    elif avail_time < total_teaching_duration:
                        self.add_warning(i, "%g available hours < %g courses hours including other deps week %s" % (
                            avail_time / 60, total_teaching_duration / 60, week))
                        # We used to forget tutor availabilities in this case...
                        # for availability_slot in week_availability_slots:
                        #     unp_slot_cost[i][availability_slot] = 0
                        #     avail_at_school_instr[i][availability_slot] = 1
                        #     avail_instr[i][availability_slot] = 1

                    elif avail_time < 2 * teaching_duration \
                            and i.status == Tutor.FULL_STAFF:
                        self.add_warning(i, "only %g available hours for %g courses hours week %s" %
                                         (avail_time / 60,
                                          teaching_duration / 60,
                                          week))
                    maximum = max([a.value for a in week_tutor_availabilities])
                    if maximum == 0:
                        for availability_slot in week_availability_slots:
                            unp_slot_cost[i][availability_slot] = 0
                            avail_at_school_instr[i][availability_slot] = 0
                            avail_instr[i][availability_slot] = 0
                        continue

                    non_prefered_duration = max(1, sum(a.duration
                                                       for a in week_tutor_availabilities if
                                                       1 <= a.value <= maximum - 1))
                    average_value = sum(a.duration * a.value
                                        for a in week_tutor_availabilities
                                        if 1 <= a.value <= maximum - 1) / non_prefered_duration

                    for availability_slot in week_availability_slots:
                        avail = set(a for a in week_tutor_availabilities
                                    if availability_slot.is_simultaneous_to(a))
                        if not avail:
                            print(f"availability pbm for {i} availability_slot {availability_slot}")
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
                                unp_slot_cost[i][availability_slot] = (value - maximum) / (average_value - maximum)

            # Add fixed_courses constraint
            for sl in self.wdb.availability_slots:
                fixed_courses = self.wdb.fixed_courses_for_tutor[i] & self.wdb.fixed_courses_for_avail_slot[sl]

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
        for course_type in self.wdb.course_types:
            for promo in self.train_prog:
                avail_course[(course_type, promo)] = {}
                non_preferred_cost_course[(course_type, promo)] = {}
                for week in self.weeks:
                    week_availability_slots = slots_filter(self.wdb.availability_slots, week=week)
                    courses_avail = set(self.wdb.courses_availabilities
                                        .filter(course_type=course_type,
                                                train_prog=promo,
                                                week=week))
                    if not courses_avail:
                        courses_avail = set(self.wdb.courses_availabilities
                                            .filter(course_type=course_type,
                                                    train_prog=promo,
                                                    week=None))
                        for cv in courses_avail:
                            cv.week = week
                    if not courses_avail:
                        for availability_slot in week_availability_slots:
                            avail_course[(course_type, promo)][availability_slot] = 1
                            non_preferred_cost_course[(course_type,
                                                           promo)][availability_slot] = 0


                    else:
                        for availability_slot in week_availability_slots:
                            avail = set(a for a in courses_avail
                                        if availability_slot.is_simultaneous_to(a))

                            if avail:
                                minimum = min(a.value for a in avail)
                                if minimum == 0:
                                    avail_course[(course_type, promo)][availability_slot] = 0
                                    non_preferred_cost_course[(course_type,
                                                                   promo)][availability_slot] = 100
                                else:
                                    avail_course[(course_type, promo)][availability_slot] = 1
                                    value = minimum
                                    non_preferred_cost_course[(course_type, promo)][availability_slot] \
                                        = 1 - value / 8

                            else:
                                avail_course[(course_type, promo)][availability_slot] = 1
                                non_preferred_cost_course[(course_type, promo)][availability_slot] = 0

        return non_preferred_cost_course, avail_course

    def compute_avail_room(self):
        avail_room = {}
        for room in self.wdb.basic_rooms:
            avail_room[room] = {}
            for sl in self.wdb.availability_slots:
                if RoomPreference.objects.filter(
                        start_time__lt=sl.start_time + sl.duration,
                        start_time__gt=sl.start_time - F('duration'),
                        day=sl.day.day,
                        week=sl.day.week,
                        room=room, value=0).exists():
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
        if not MinNonPreferedTutorsSlot.objects.filter(department=self.department).exists():
            M = MinNonPreferedTutorsSlot.objects.create(weight=max_weight, department=self.department)


        # second objective  => minimise use of unpreferred slots for courses
        # ponderation MIN_UPS_C
        if not MinNonPreferedTrainProgsSlot.objects.filter(department=self.department).exists():
            M = MinNonPreferedTrainProgsSlot.objects.create(weight=max_weight, department=self.department)

    @timer
    def add_other_departments_constraints(self):
        """
        Add the constraints imposed by other departments' scheduled courses.
        """

        for sl in self.wdb.availability_slots:
            # constraint : other_departments_sched_courses rooms are not available
            for r in self.wdb.basic_rooms:
                other_dep_sched_courses = self.wdb.other_departments_sched_courses_for_room[r] \
                                    & self.wdb.other_departments_sched_courses_for_avail_slot[sl]
                if other_dep_sched_courses:
                    self.avail_room[r][sl] = 0

        for sl in self.wdb.availability_slots:
            # constraint : other_departments_sched_courses instructors are not available
            for i in self.wdb.instructors:
                other_dep_sched_courses = ((self.wdb.other_departments_scheduled_courses_for_tutor[i]
                                      | self.wdb.other_departments_scheduled_courses_for_supp_tutor[i])
                                     & self.wdb.other_departments_sched_courses_for_avail_slot[sl])

                if other_dep_sched_courses:
                    self.avail_instr[i][sl] = 0

    def add_specific_constraints(self):
        """
        Add the active specific constraints stored in the database.
        """

        for week in self.weeks:
            for constr in get_ttconstraints(
                    self.department,
                    week=week,
                    # train_prog=promo,
                    is_active=True):
                if not self.core_only or constr.__class__ in [AssignAllCourses, ScheduleAllCourses,
                                                              NoSimultaneousGroupCourses]:
                    print(constr.__class__.__name__, constr.id, end=' - ')
                    timer(constr.enrich_ttmodel)(self, week)

        if self.pre_assign_rooms and not self.core_only:
            for week in self.weeks:
                #Consider RoomConstraints that have enrich_ttmodel method
                for constr in get_room_constraints(
                        self.department,
                        week=week,
                        is_active=True):
                    if hasattr(constr, 'enrich_ttmodel'):
                        print(constr.__class__.__name__, constr.id, end=' - ')
                        timer(constr.enrich_ttmodel)(self, week)

    def update_objective(self):
        self.obj = self.lin_expr()
        for week in self.weeks + [None]:
            for i in self.wdb.instructors:
                self.obj += self.cost_I[i][week]
            for g in self.wdb.basic_groups:
                self.obj += self.cost_G[g][week]
            self.obj += self.generic_cost[week]
        for sl in self.wdb.courses_slots:
            self.obj += self.cost_SL[sl]
        self.set_objective(self.obj)

    def add_TT_constraints(self):
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

    def add_tt_to_db(self, target_work_copy):

        close_old_connections()
        # remove target working copy
        ScheduledCourse.objects \
            .filter(course__module__train_prog__department=self.department,
                    course__week__in=self.weeks,
                    work_copy=target_work_copy) \
            .delete()

        if self.department.mode.cosmo == 2:
            corresponding_group = {}
            for i in self.wdb.instructors:
                corresponding_group[i] = self.wdb.groups.get(name=i.username)
            for c in self.wdb.courses:
                c.groups.clear()

        for c in self.wdb.courses:
            for sl in self.wdb.compatible_slots[c]:
                if self.get_var_value(self.TT[(sl, c)]) == 1:
                    cp = ScheduledCourse(course=c,
                                         start_time=sl.start_time,
                                         day=sl.day.day,
                                         work_copy=target_work_copy)
                    for i in self.wdb.possible_tutors[c]:
                        if self.get_var_value(self.TTinstructors[(sl, c, i)]) == 1:
                            cp.tutor = i
                            if self.department.mode.cosmo == 2:
                                c.groups.add(corresponding_group[i])
                            break
                    if not self.department.mode.cosmo:
                        if self.pre_assign_rooms:
                            for rg in self.wdb.course_rg_compat[c]:
                                if self.get_var_value(self.TTrooms[(sl, c, rg)]) == 1:
                                    cp.room = rg
                                    break
                    cp.save()

        for fc in self.wdb.fixed_courses:
            cp = ScheduledCourse(course=fc.course,
                                 start_time=fc.start_time,
                                 day=fc.day,
                                 room=fc.room,
                                 work_copy=target_work_copy,
                                 tutor=fc.tutor)
            if ScheduledCourseAdditional.objects.filter(scheduled_course__id=fc.id).exists():
                sca = fc.additional
                sca.pk = None
                sca.scheduled_course = cp
                sca.save()
            cp.save()

        # # On enregistre les coûts dans la BDD
        TutorCost.objects.filter(department=self.department,
                                 week__in=self.wdb.weeks,
                                 work_copy=target_work_copy).delete()
        GroupFreeHalfDay.objects.filter(group__train_prog__department=self.department,
                                        week__in=self.wdb.weeks,
                                        work_copy=target_work_copy).delete()
        GroupCost.objects.filter(group__train_prog__department=self.department,
                                 week__in=self.wdb.weeks,
                                 work_copy=target_work_copy).delete()

        for week in self.weeks:
            for i in self.wdb.instructors:
                tc = TutorCost(department=self.department,
                               tutor=i,
                               week=week,
                               value=self.get_expr_value(self.cost_I[i][week]),
                               work_copy=target_work_copy)
                tc.save()

            for g in self.wdb.basic_groups:
                DJL = 0
                if Time.PM in self.possible_apms:
                    DJL += self.get_expr_value(self.FHD_G[Time.PM][g][week])
                if Time.AM in self.possible_apms:
                    DJL += 0.01 * self.get_expr_value(self.FHD_G[Time.AM][g][week])

                djlg = GroupFreeHalfDay(group=g,
                                        week=week,
                                        work_copy=target_work_copy,
                                        DJL=DJL)
                djlg.save()
                cg = GroupCost(group=g,
                               week=week,
                               work_copy=target_work_copy,
                               value=self.get_expr_value(self.cost_G[g][week]))
                cg.save()

    # Some extra Utils
    def solution_files_prefix(self):
        return f"flopmodel_{self.department.abbrev}_{'_'.join(str(w) for w in self.weeks)}"

    def add_tt_to_db_from_file(self, filename=None, target_work_copy=None):
        if filename is None:
            filename = self.last_counted_solution_filename()
        if target_work_copy is None:
            target_work_copy = self.choose_free_work_copy()
        close_old_connections()
        # remove target working copy
        ScheduledCourse.objects \
            .filter(course__module__train_prog__department=self.department,
                    course__week__in=self.weeks,
                    work_copy=target_work_copy) \
            .delete()

        print("Added work copy #%g" % target_work_copy)
        solution_file_one_vars_set = self.read_solution_file(filename)

        for c in self.wdb.courses:
            for sl in self.wdb.compatible_slots[c]:
                for i in self.wdb.possible_tutors[c]:
                    if self.TTinstructors[(sl, c, i)].getName() in solution_file_one_vars_set:
                        cp = ScheduledCourse(course=c,
                                             tutor=i,
                                             start_time=sl.start_time,
                                             day=sl.day.day,
                                             work_copy=target_work_copy)
                        if self.pre_assign_rooms:
                            for rg in self.wdb.course_rg_compat[c]:
                                if self.TTrooms[(sl, c, rg)].getName() in solution_file_one_vars_set:
                                    cp.room = rg
                                    break
                        cp.save()

        for fc in self.wdb.fixed_courses:
            cp = ScheduledCourse(course=fc.course,
                                 start_time=fc.start_time,
                                 day=fc.day,
                                 room=fc.room,
                                 work_copy=target_work_copy,
                                 tutor=fc.tutor)
            cp.save()

    def solve(self, time_limit=None, target_work_copy=None, solver=GUROBI_NAME, threads=None, ignore_sigint=True):
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

            if target_work_copy is None:
                if self.department.mode.cosmo == 2:
                    target_work_copy = 0
                else:
                    target_work_copy = self.choose_free_work_copy()

            self.add_tt_to_db(target_work_copy)
            print("Added work copy N°%g" % target_work_copy)
            if self.post_assign_rooms:
                RoomModel(self.department.abbrev, self.weeks, target_work_copy).solve()
                print("Rooms assigned")
            return target_work_copy

    def find_same_course_slot_in_other_week(self, slot, week):
        other_slots = slots_filter(self.wdb.courses_slots, week=week, same=slot)
        if len(other_slots) != 1:
            raise Exception(f"Wrong slots among weeks {week}, {slot.day.week} \n {slot} vs {other_slots}")
        return other_slots.pop()