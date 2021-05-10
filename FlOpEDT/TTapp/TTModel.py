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
import os, fnmatch, re

from django.core.mail import EmailMessage
from pulp import LpVariable, LpConstraint, LpBinary, LpConstraintEQ, \
    LpConstraintGE, LpConstraintLE, LpAffineExpression, LpProblem, LpStatus, \
    LpMinimize, lpSum, LpStatusOptimal, LpStatusNotSolved

import pulp
from pulp import GUROBI_CMD

from base.models import Group, \
    Room, RoomSort, RoomType, RoomPreference, \
    Course, ScheduledCourse, UserPreference, CoursePreference, \
    Department, Module, TrainingProgramme, CourseType, \
    Dependency, TutorCost, GroupFreeHalfDay, GroupCost, Holiday, TrainingHalfDay, \
    CourseStartTimeConstraint, TimeGeneralSettings, ModulePossibleTutors, CoursePossibleTutors, \
    ModuleTutorRepartition, ScheduledCourseAdditional

from base.timing import Time

from people.models import Tutor

from TTapp.models import MinNonPreferedTutorsSlot, Stabilize, MinNonPreferedTrainProgsSlot

from TTapp.slots import slots_filter, days_filter

from TTapp.weeks_database import WeeksDatabase

from MyFlOp.MyTTUtils import reassign_rooms

import signal

from django.db import close_old_connections
from django.db.models import Q, Max, F
from django.conf import settings

import datetime

import logging

from TTapp.ilp_constraints.constraintManager import ConstraintManager
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType

from TTapp.ilp_constraints.constraints.dependencyConstraint import DependencyConstraint
from TTapp.ilp_constraints.constraints.instructorConstraint import InstructorConstraint
from TTapp.ilp_constraints.constraints.simulSlotGroupConstraint import SimulSlotGroupConstraint
from TTapp.ilp_constraints.constraints.slotInstructorConstraint import SlotInstructorConstraint
from TTapp.ilp_constraints.constraints.courseConstraint import CourseConstraint

logger = logging.getLogger(__name__)
pattern = r".+: (.|\s)+ (=|>=|<=) \d*"
GUROBI = 'GUROBI'
GUROBI_NAME = 'GUROBI_CMD'
solution_files_path = "misc/logs/solutions"

class TTModel(object):
    def __init__(self, department_abbrev, week_year_list,
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
                 min_visio=0.5):
        # beg_file = os.path.join('logs',"FlOpTT")
        self.department = Department.objects.get(abbrev=department_abbrev)

        # Split week_year_list into weeks (list), and year (int)
        # week_year should be a list of {'week': week, 'year': year}
        year = None
        weeks = []
        for week_year in week_year_list:
            y = week_year['year']
            w = week_year['week']
            if year is None: year = y
            weeks.append(w)
            if year != y:
              raise Exception("Multiple week selection only support same year")

        self.weeks = weeks
        self.year = year

        # Create the PuLP model, giving the name of the lp file
        self.model = LpProblem(self.solution_files_prefix(), LpMinimize)
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
        self.keep_many_solution_files = keep_many_solution_files
        self.min_visio = min_visio
        self.var_nb = 0
        self.constraintManager = ConstraintManager()

        print("\nLet's start weeks #%s" % weeks)

        print("Initialisation...")
        a = datetime.datetime.now()
        self.warnings = {}

        if train_prog is None:
            train_prog = TrainingProgramme.objects.filter(department=self.department)
        else:
            try:
                _ = iter(train_prog)
            except TypeError:
                train_prog = TrainingProgramme.objects.filter(id=train_prog.id)
            print('Will modify only courses of training programme(s) ', train_prog)
        self.train_prog = train_prog
        self.stabilize_work_copy = stabilize_work_copy
        self.obj = self.lin_expr()
        self.wdb = self.wdb_init()
        self.possible_apms = self.wdb.possible_apms
        self.cost_I, self.FHD_G, self.cost_G, self.cost_SL, self.generic_cost = self.costs_init()
        self.TT, self.TTrooms, self.TTinstructors = self.TT_vars_init()
        self.IBD, self.IBD_GTE, self.IBHD, self.GBHD, self.IBS, self.forced_IBD = self.busy_vars_init()
        if self.department.mode.visio:
            self.physical_presence, self.has_visio = self.visio_vars_init()
        self.avail_instr, self.avail_at_school_instr, self.unp_slot_cost \
            = self.compute_non_preferred_slots_cost()
        self.unp_slot_cost_course, self.avail_course \
            = self.compute_non_preferred_slots_cost_course()
        self.avail_room = self.compute_avail_room()
        print('Ok', datetime.datetime.now()-a)
        self.one_var = self.add_var()
        self.add_constraint(self.one_var, '==', 1, Constraint(constraint_type=ConstraintType.TECHNICAL))

        # Hack : permet que ça marche même si les dispos sur la base sont pas complètes
        for i in self.wdb.instructors:
            for availability_slot in self.wdb.availability_slots:
                if availability_slot not in self.avail_instr[i]:
                    self.avail_instr[i][availability_slot] = 0
                if availability_slot not in self.unp_slot_cost[i]:
                    self.unp_slot_cost[i][availability_slot] = 0

        self.add_TT_constraints()

        if self.warnings:
            print("Relevant warnings :")
            for key, key_warnings in self.warnings.items():
                print("%s : %s" % (key, ", ".join([str(x) for x in key_warnings])))

        if self.send_mails:
            self.send_lack_of_availability_mail()

    def wdb_init(self):
        wdb = WeeksDatabase(self.department, self.weeks, self.year, self.train_prog, self.slots_step)
        return wdb

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

    def TT_vars_init(self):
        TT = {}
        TTrooms = {}
        TTinstructors = {}

        for sl in self.wdb.courses_slots:
            for c in self.wdb.compatible_courses[sl]:
                # print c, c.room_type
                TT[(sl, c)] = self.add_var("TT(%s,%s)" % (sl, c))
                for rg in self.wdb.course_rg_compat[c]:
                    TTrooms[(sl, c, rg)] \
                        = self.add_var("TTroom(%s,%s,%s)" % (sl, c, rg))
                for i in self.wdb.possible_tutors[c]:
                    TTinstructors[(sl, c, i)] \
                        = self.add_var("TTinstr(%s,%s,%s)" % (sl, c, i))
        return TT, TTrooms, TTinstructors

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
                                        Constraint(constraint_type=ConstraintType.IBD_INF, instructors=i, days=d))

        forced_IBD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                forced_IBD[(i, d)] = 0
                if d.day in self.wdb.physical_presence_days_for_tutor[i][d.week]:
                    forced_IBD[(i, d)] = 1
                if self.department.mode.cosmo:
                    if self.wdb.sched_courses.filter(day=d.day, course__week=d.week,
                                                     course__suspens=False,
                                                     course__tutor=i).exists():
                        forced_IBD[(i, d)] = 1

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
        for g in self.wdb.basic_groups:
            for d in self.wdb.days:
                # add constraint linking IBD to EDT
                for apm in self.possible_apms:
                    GBHD[(g, d, apm)] \
                        = self.add_var("GBHD(%s,%s,%s)" % (g, d, apm))
                    halfdayslots = slots_filter(self.wdb.courses_slots, day=d, apm=apm)
                    card = 2 * len(halfdayslots)
                    expr = self.lin_expr()
                    expr += card * GBHD[(g, d, apm)]
                    for sl in halfdayslots:
                        for c in self.wdb.courses_for_group[g] & self.wdb.compatible_courses[sl]:
                            expr -= self.TT[(sl, c)]
                        for sg in g.ancestor_groups():
                            for c in self.wdb.courses_for_group[sg] & self.wdb.compatible_courses[sl]:
                                expr -= self.TT[(sl, c)]
                    self.add_constraint(expr, '>=', 0,
                                        Constraint(constraint_type=ConstraintType.GBHD_INF, groups=g, days=d))
                    self.add_constraint(expr, '<=', card - 1,
                                        Constraint(constraint_type=ConstraintType.GBHD_SUP, groups=g, days=d))

        return IBD, IBD_GTE, IBHD, GBHD, IBS, forced_IBD

    def visio_vars_init(self):
        physical_presence = {g: {(d, apm): self.add_var()
                                for d in self.wdb.days for apm in [Time.AM, Time.PM]}
                             for g in self.wdb.basic_groups}

        for g in self.wdb.basic_groups:
            for (d, apm) in physical_presence[g]:
                expr = 1000 * physical_presence[g][d, apm] \
                       - self.sum(self.TTrooms[sl, c, r]
                                  for c in self.wdb.courses_for_basic_group[g]
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
                                  for c in self.wdb.courses_for_basic_group[g]
                                  for sl in slots_filter(self.wdb.compatible_slots[c], day=d, apm=apm))
                self.add_constraint(expr, '<=', 999,
                                    Constraint(constraint_type=ConstraintType.HAS_VISIO, groups=g, days=d, apm=apm))
                self.add_constraint(expr, '>=', 0,
                                    Constraint(constraint_type=ConstraintType.HAS_VISIO, groups=g, days=d, apm=apm))

        return physical_presence, has_visio

    def add_var(self, name=''):
        """
        Create a PuLP binary variable
        """
        # return LpVariable(name, lowBound = 0, upBound = 1, cat = LpBinary)
        # countedname = name + '_' + str(self.var_nb)
        self.var_nb += 1

        # return LpVariable(countedname, cat=LpBinary)
        return LpVariable(str(self.var_nb), cat=LpBinary)

    def add_constraint(self, expr, relation, value, constraint=Constraint()):
        constraint_id = self.constraintManager.get_nb_constraints()

        # Add mathematic constraint
        if relation == '==':
            pulp_relation = LpConstraintEQ
        elif relation == '<=':
            pulp_relation = LpConstraintLE
        elif relation == '>=':
            pulp_relation = LpConstraintGE
        else:
            raise Exception("relation must be either '==' or '>=' or '<='")
        self.model += LpConstraint(e=expr, sense=pulp_relation,
                                   rhs=value, name=str(constraint_id))

        # Add intelligible constraint
        constraint.id = constraint_id
        self.constraintManager.add_constraint(constraint)

    def lin_expr(self, expr=None):
        return LpAffineExpression(expr)

    def sum(self, *args):
        return lpSum(list(*args))

    def check_and_sum(self, dict, *args):
        """
        This helper method get a variable list check if the corresponding
        expression exists in the given dict and returns the lpSum of
        available expressions
        """
        expressions = [dict(v) for v in args if v in dict]
        return lpSum(expressions)

    def get_var_value(self, ttvar):
        return round(ttvar.value())

    def get_expr_value(self, ttexpr):
        return ttexpr.value()

    def get_obj_coeffs(self):
        """
        get the coeff of each var in the objective
        """
        l = [(weight, var) for (var, weight) in self.obj.items()
             if var.value() != 0 and round(weight) != 0]
        l.sort(reverse=True)
        return l

    def set_objective(self, obj):
        self.model.setObjective(obj)

    def get_constraint(self, name):
        return self.model.constraints[name]

    def get_all_constraints(self):
        return self.model.constraints

    def remove_constraint(self, constraint_name):
        del self.model.constraints[constraint_name]

    def var_coeff(self, var, constraint):
        return constraint[var]

    def change_var_coeff(self, var, constraint, newvalue):
        constraint[var] = newvalue

    def add_conjunct(self, v1, v2):
        """
        Crée une nouvelle variable qui est la conjonction des deux
        et l'ajoute au modèle
        """
        l_conj_var = self.add_var("%s AND %s" % (str(v1), str(v2)))
        self.add_constraint(l_conj_var - (v1 + v2), '>=', -1,
                            Constraint(constraint_type=ConstraintType.CONJONCTION))
        self.add_constraint(2 * l_conj_var - (v1 + v2), '<=', 0,
                            Constraint(constraint_type=ConstraintType.CONJONCTION))
        return l_conj_var

    def add_floor(self, expr, floor, bound):
        """
        Add a variable that equals 1 if expr >= floor, if integer expr is
        known to be within [0, bound]
        """
        l_floor = self.add_var()
        self.add_constraint(expr - l_floor * floor, '>=', 0,
                            Constraint(constraint_type=ConstraintType.SEUIL))
        self.add_constraint(l_floor * bound - expr, '>=', 1 - floor,
                            Constraint(constraint_type=ConstraintType.SEUIL))
        return l_floor

    def add_if_var_a_then_not_vars_b_constraint(self, var_a, vars_b_list, name_of_b_list=None):
        bound = len(vars_b_list) + 1
        if name_of_b_list is None:
            name_of_b_list = "anonymous list"
        # , 'If %s then not any of %s_%g' % (var_a, name_of_b_list, self.constraint_nb)
        self.add_constraint(bound * var_a + self.sum(var for var in vars_b_list), '<=', bound,
                            Constraint(constraint_type=ConstraintType.SI_A_ALORS_NON_B))

    def add_to_slot_cost(self, slot, cost):
        self.cost_SL[slot] += cost

    def add_to_inst_cost(self, instructor, cost, week=None):
        self.cost_I[instructor][week] += cost

    def add_to_group_cost(self, group, cost, week=None):
        self.cost_G[group][week] += cost

    def add_to_generic_cost(self, cost, week=None):
        self.generic_cost[week] += cost

    def add_warning(self, key, warning):
        if key in self.warnings:
            self.warnings[key].append(warning)
        else:
            self.warnings[key] = [warning]

    def add_stabilization_constraints(self):

        # maximize stability
        if self.stabilize_work_copy is not None:
            s = Stabilize(general=True,
                          work_copy=self.stabilize_work_copy)
            s.save()
            for week in self.weeks:
                s.enrich_model(self, week, self.max_stab)
            s.delete()
            print('Will stabilize from remote work copy #', \
                  self.stabilize_work_copy)
        else:
            print('No stabilization')

    def add_core_constraints(self):
        """
        Add the core constraints to the PuLP model :
            - a course is scheduled once and only once
            - no group has two courses in parallel
            - + a teacher does not have 2 courses in parallel
              + the teachers are available on the chosen slots
            - no course on vacation days
        """

        print("adding core constraints")

        # constraint : only one course on simultaneous slots
        print('Simultaneous slots constraints for groups')
        for sl in self.wdb.availability_slots:
            for bg in self.wdb.basic_groups:
                self.add_constraint(self.sum(self.TT[(sl2, c2)]
                                             for sl2 in slots_filter(self.wdb.courses_slots,
                                                                     simultaneous_to=sl)
                                             for c2 in self.wdb.courses_for_basic_group[bg]
                                             & self.wdb.compatible_courses[sl2]),
                                    '<=', 1, SimulSlotGroupConstraint(sl, bg))

        # a course is scheduled once and only once
        for c in self.wdb.courses:
            self.add_constraint(self.sum([self.TT[(sl, c)] for sl in self.wdb.compatible_slots[c]]), '==', 1,
                                CourseConstraint(c))

        # # Training half day TODO: Delete usage because redundant with NoCourseOnDay ?
        # for training_half_day in self.wdb.training_half_days:
        #     training_slots = slots_filter(self.wdb.courses_slots, week_day=training_half_day.day, week=training_half_day.week)
        #     if training_half_day.apm is not None:
        #         training_slots = slots_filter(training_slots, apm=training_half_day.apm)
        #     training_progs = self.train_prog
        #     if training_half_day.train_prog is not None:
        #         training_progs = [training_half_day.train_prog]
        #     # , "no_course_on_%s_%s_%g" % (training_half_day.day, training_half_day.apm, self.constraint_nb)
        #     self.add_constraint(self.sum(self.TT[(sl, c)] for sl in training_slots
        #                                  for c in self.wdb.compatible_courses[sl]
        #                                  & set(self.wdb.courses.filter(module__train_prog__in=training_progs))),
        #                         '==', 0,
        #                         Constraint(constraint_type=ConstraintType.PAS_DE_COURS_DE_DEMI_JOURNEE,
        #                         days=training_half_day.day, apm=training_half_day.apm))

    def add_instructors_constraints(self):
        print("adding instructors constraints")

        # Each course is assigned to a unique tutor
        for c in self.wdb.courses:
            for sl in self.wdb.compatible_slots[c]:
                self.add_constraint(self.sum(self.TTinstructors[(sl, c, i)]
                                             for i in self.wdb.possible_tutors[c]) - self.TT[sl, c],
                                    '==', 0,
                                    InstructorConstraint(constraint_type=ConstraintType.COURS_DOIT_AVOIR_PROFESSEUR,
                                    slot=sl, course=c))

        if self.core_only:
            return

        for i in self.wdb.instructors:
            if i.username == '---':
                continue
            for sl in self.wdb.availability_slots:
                # a course is assigned to a tutor only if s⋅he is available
                self.add_constraint(self.sum(self.TTinstructors[(sl2, c2, i)]
                                             for sl2 in slots_filter(self.wdb.courses_slots, simultaneous_to=sl)
                                             for c2 in self.wdb.possible_courses[i] & self.wdb.compatible_courses[sl2]),
                                    '<=', self.avail_instr[i][sl],
                                    SlotInstructorConstraint(sl, i))

                self.add_constraint(self.sum(self.TT[(sl2, c2)]
                                             for sl2 in slots_filter(self.wdb.courses_slots, simultaneous_to=sl)
                                             for c2 in self.wdb.courses_for_supp_tutor[i]
                                             & self.wdb.compatible_courses[sl2]),
                                    '<=', self.avail_instr[i][sl],
                                    Constraint(constraint_type=ConstraintType.SUPP_TUTOR,
                                               instructors=i, slots=sl))

                if self.department.mode.visio:
                    # avail_at_school_instr consideration...
                    relevant_courses = set(c for c in self.wdb.possible_courses[i]
                                           if None in self.wdb.course_rg_compat[c])
                    self.add_constraint(
                        self.sum(self.TTinstructors[(sl2, c2, i)] - self.TTrooms[(sl2, c2, None)]
                                 for sl2 in slots_filter(self.wdb.courses_slots, simultaneous_to=sl)
                                 for c2 in relevant_courses & self.wdb.compatible_courses[sl2]),
                        '<=', self.avail_at_school_instr[i][sl],
                        SlotInstructorConstraint(sl, i)
                    )

        for mtr in ModuleTutorRepartition.objects.filter(module__in=self.wdb.modules,
                                                         week__in=self.weeks,
                                                         year=self.year):
            self.add_constraint(
                self.sum(self.TTinstructors[sl, c, mtr.tutor]
                         for c in set(c for c in self.wdb.courses if c.module == mtr.module
                                      and c.type == mtr.course_type and c.tutor is None)
                         for sl in slots_filter(self.wdb.compatible_slots[c],
                                                week=mtr.week)
                         ),
                '==', mtr.courses_nb, Constraint()
            )

    def add_rooms_constraints(self):
        print("adding room constraints")
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

    def add_visio_room_constraints(self):

        # courses that are neither visio neither no-visio are preferentially not in Visio room
        for bg in self.wdb.basic_groups:
            group_courses_except_visio_and_no_visio_ones = \
                self.wdb.courses_for_basic_group[bg] - self.wdb.visio_courses - self.wdb.no_visio_courses
            self.add_to_group_cost(bg,
                                   self.min_visio *
                                   self.sum(self.TTrooms[(sl, c, None)] * self.wdb.visio_ponderation[c]
                                            for c in group_courses_except_visio_and_no_visio_ones
                                            for sl in self.wdb.compatible_slots[c])
                                   )

        # visio-courses are preferentially in Visio
        for bg in self.wdb.basic_groups:
            group_visio_courses= \
                self.wdb.courses_for_basic_group[bg] & self.wdb.visio_courses
            self.add_to_group_cost(bg,
                                   self.min_visio *
                                   self.sum(self.TTrooms[(sl, c, room)] * self.wdb.visio_ponderation[c]
                                            for c in group_visio_courses
                                            for room in self.wdb.course_rg_compat[c] - {None}
                                            for sl in self.wdb.compatible_slots[c])
                                   )

        # No visio_course have (strongly) preferentially a room
        for bg in self.wdb.basic_groups:
            group_no_visio_courses = self.wdb.courses_for_basic_group[bg] & self.wdb.no_visio_courses
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
                if not self.department.mode.cosmo and week_holidays:
                    week_tutor_availabilities = set(
                        a for a in self.wdb.availabilities[i][week]
                        if a.day not in week_holidays)
                else:
                    week_tutor_availabilities = self.wdb.availabilities[i][week]

                if not week_tutor_availabilities:
                    self.add_warning(i, "no availability information given week %g" % week)
                    for availability_slot in week_availability_slots:
                        unp_slot_cost[i][availability_slot] = 0
                        avail_at_school_instr[i][availability_slot] = 1
                        avail_instr[i][availability_slot] = 1

                else:
                    avail_time = sum(a.duration for a in week_tutor_availabilities if a.value >= 1)

                    if avail_time < teaching_duration:
                        self.add_warning(i, "%g available hours < %g courses hours week %g" %
                                         (avail_time / 60, teaching_duration / 60, week))
                        # We used to forget tutor availabilities in this case...
                        # for availability_slot in week_availability_slots:
                        #     unp_slot_cost[i][availability_slot] = 0
                        #     avail_at_school_instr[i][availability_slot] = 1
                        #     avail_instr[i][availability_slot] = 1

                    elif avail_time < total_teaching_duration:
                        self.add_warning(i, "%g available hours < %g courses hours including other deps week %g" % (
                            avail_time / 60, total_teaching_duration / 60, week))
                        # We used to forget tutor availabilities in this case...
                        # for availability_slot in week_availability_slots:
                        #     unp_slot_cost[i][availability_slot] = 0
                        #     avail_at_school_instr[i][availability_slot] = 1
                        #     avail_instr[i][availability_slot] = 1

                    elif avail_time < 2 * teaching_duration \
                            and i.status == Tutor.FULL_STAFF:
                        self.add_warning(i, "only %g available hours for %g courses hours week %g" %
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
                                    if a.start_time < availability_slot.end_time
                                    and availability_slot.start_time < a.start_time + a.duration
                                    and a.day == availability_slot.day.day)
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
                    if not courses_avail:
                        # print("No course availability given for %s - %s" % (course_type, promo))
                        for availability_slot in week_availability_slots:
                            avail_course[(course_type, promo)][availability_slot] = 1
                            non_preferred_cost_course[(course_type,
                                                           promo)][availability_slot] = 0
                    else:
                        for availability_slot in week_availability_slots:
                            try:
                                avail = set(a for a in courses_avail
                                            if a.start_time < availability_slot.end_time
                                            and availability_slot.start_time < a.start_time + a.duration
                                            and a.day == availability_slot.day.day)

                                if avail:
                                    minimum = min(a.value for a in avail)
                                    if minimum == 0:
                                        avail_course[(course_type, promo)][availability_slot] = 0
                                        non_preferred_cost_course[(course_type,
                                                                       promo)][availability_slot] = 5
                                    else:
                                        avail_course[(course_type, promo)][availability_slot] = 1
                                        value = minimum
                                        non_preferred_cost_course[(course_type, promo)][availability_slot] \
                                            = 1 - value / 8

                                else:
                                    avail_course[(course_type, promo)][availability_slot] = 1
                                    non_preferred_cost_course[(course_type, promo)][availability_slot] = 0

                            except:
                                avail_course[(course_type, promo)][availability_slot] = 1
                                non_preferred_cost_course[(course_type, promo)][availability_slot] = 0
                                print("Course availability problem for %s - %s on availability_slot %s" % (
                                    course_type, promo, availability_slot))

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
                        year=self.year,
                        room=room, value=0).exists():
                    avail_room[room][sl] = 0
                else:
                    avail_room[room][sl] = 1

        return avail_room

    def add_slot_preferences(self):
        """
         Add the constraints derived from the slot preferences expressed on the database
         """
        print("adding slot preferences")
        from TTapp.TTConstraint import max_weight
        # first objective  => minimise use of unpreferred slots for teachers
        # ponderation MIN_UPS_I

        M, created = MinNonPreferedTutorsSlot.objects.get_or_create(weight=max_weight, department=self.department)
        if created:
            M.save()

        # second objective  => minimise use of unpreferred slots for courses
        # ponderation MIN_UPS_C
        M, created = MinNonPreferedTrainProgsSlot.objects.get_or_create(weight=max_weight, department=self.department)
        if created:
            M.save()

    def add_other_departments_constraints(self):
        """
        Add the constraints imposed by other departments' scheduled courses.
        """
        print("adding other departments constraints")
        for sl in self.wdb.availability_slots:
            # constraint : other_departments_sched_courses rooms are not available
            for r in self.wdb.basic_rooms:
                other_dep_sched_courses = self.wdb.other_departments_sched_courses_for_room[r] \
                                    & self.wdb.other_departments_sched_courses_for_avail_slot[sl]
                if other_dep_sched_courses:
                    self.avail_room[r][sl] = 0

        if self.core_only:
            return

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
        print("adding active specific constraints")
        for week in self.weeks:
            for constr in get_constraints(
                    self.department,
                    week=week,
                    year=self.year,
                    # train_prog=promo,
                    is_active=True):
                constr.enrich_model(self, week)

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

        self.add_rooms_constraints()

        self.add_instructors_constraints()

        if self.core_only:
            return

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
                    course__year=self.year,
                    work_copy=target_work_copy) \
            .delete()

        for c in self.wdb.courses:
            for sl in self.wdb.compatible_slots[c]:
                for i in self.wdb.possible_tutors[c]:
                    if self.get_var_value(self.TTinstructors[(sl, c, i)]) == 1:
                        # No = len(self.wdb.sched_courses \
                        #          .filter(course__module=c.module,
                        #                  course__group=c.group,
                        #                  course__week__lte=self.weeks - 1,
                        #                  copie_travail=0))
                        # No += len(CoursPlace.objects \
                        #           .filter(course__module=c.module,
                        #                   course__group=c.group,
                        #                   course__week=self.weeks,
                        #                   copie_travail=target_work_copy))
                        cp = ScheduledCourse(course=c,
                                             tutor=i,
                                             start_time=sl.start_time,
                                             day=sl.day.day,
                                             work_copy=target_work_copy)

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
                                 year=self.wdb.year,
                                 work_copy=target_work_copy).delete()
        GroupFreeHalfDay.objects.filter(group__train_prog__department=self.department,
                                        week__in=self.wdb.weeks,
                                        year=self.wdb.year,
                                        work_copy=target_work_copy).delete()
        GroupCost.objects.filter(group__train_prog__department=self.department,
                                 week__in=self.wdb.weeks,
                                 year=self.wdb.year,
                                 work_copy=target_work_copy).delete()

        for week in self.weeks:
            for i in self.wdb.instructors:
                tc = TutorCost(department=self.department,
                               tutor=i,
                               year=self.wdb.year,
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
                                        year=self.wdb.year,
                                        week=week,
                                        work_copy=target_work_copy,
                                        DJL=DJL)
                djlg.save()
                cg = GroupCost(group=g,
                               year=self.wdb.year,
                               week=week,
                               work_copy=target_work_copy,
                               value=self.get_expr_value(self.cost_G[g][week]))
                cg.save()

    # Some extra Utils

    def solution_files_prefix(self):
        return f"flopmodel_{self.department.abbrev}_{'_'.join(str(w) for w in self.weeks)}"

    def all_counted_solution_files(self):
        solution_file_pattern = f"{self.solution_files_prefix()}_*.sol"
        result = []
        for root, dirs, files in os.walk(solution_files_path):
            for name in files:
                if fnmatch.fnmatch(name, solution_file_pattern):
                    result.append(os.path.join(root, name))
        result.sort(key=lambda filename: int(filename.split('_')[-1].split('.')[0]))
        return result

    def last_counted_solution_filename(self):
        return self.all_counted_solution_files()[-1]

    def delete_solution_files(self, all=False):
        solution_files = self.all_counted_solution_files()
        if solution_files:
            for f in solution_files[:-1]:
                os.remove(f)
            if all:
                os.remove(solution_files[-1])

    @staticmethod
    def read_solution_file(filename):
        one_vars = set()
        with open(filename) as f:
            lines = f.readlines()
            print(lines[1])
            for line in lines[2:]:
                r = line.strip().split(" ")
                if int(r[1]) == 1:
                    one_vars.add(r[0])
        return one_vars

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
                    course__year=self.year,
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

    def choose_free_work_copy(self):
        close_old_connections()

        local_max_wc = ScheduledCourse \
            .objects \
            .filter(
            course__module__train_prog__department=self.department,
            course__week__in=self.weeks,
            course__year=self.year) \
            .aggregate(Max('work_copy'))['work_copy__max']

        if local_max_wc is None:
            local_max_wc = -1

        return local_max_wc + 1

    def write_infaisability(self, write_iis=True, write_analysis=True):
        file_path = "misc/logs/iis"
        filename_suffixe = "_%s_%s" % (self.department.abbrev, self.weeks)
        iis_filename = "%s/IIS%s.ilp" % (file_path, filename_suffixe)
        if write_iis:
            from gurobipy import read
            lp = f"{self.solution_files_prefix()}-pulp.lp"
            m = read(lp)
            m.computeIIS()
            m.write(iis_filename)
        if write_analysis:
            self.constraintManager.handle_reduced_result(iis_filename, file_path, filename_suffixe)

    def optimize(self, time_limit, solver, presolve=2, threads=None):
        # The solver value shall be one of the available
        # solver corresponding pulp command or contain
        # gurobi
        if 'gurobi' in solver.lower() and hasattr(pulp, GUROBI_NAME):
            # ignore SIGINT while solver is running
            # => SIGINT is still delivered to the solver, which is what we want
            self.delete_solution_files(all=True)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            solver = GUROBI_NAME
            options = [("Presolve", presolve),
                       ("MIPGapAbs", 0.2)]
            if time_limit is not None:
                options.append(("TimeLimit", time_limit))
            if threads is not None:
                options.append(("Threads",threads))
            if self.keep_many_solution_files:
                options.append(('SolFiles',
                                f"{solution_files_path}/{self.solution_files_prefix()}"))
            result = self.model.solve(GUROBI_CMD(keepFiles=1,
                                                 msg=True,
                                                 options=options))
            if result is None or result == 0:
                self.write_infaisability()

        elif hasattr(pulp, solver):
            # raise an exception when the solver name is incorrect
            command = getattr(pulp, solver)
            self.model.solve(command(keepFiles=1,
                                     msg=True,
                                     presolve=presolve,
                                     maxSeconds=time_limit))
        else:
            print(f'Solver {solver} not found.')
            return None

        status = self.model.status
        print(LpStatus[status])
        if status == LpStatusOptimal or (solver != GUROBI_NAME and status == LpStatusNotSolved):
            return self.get_obj_coeffs()

        else:
            print(f'lpfile has been saved in {self.solution_files_prefix()}-pulp.lp')
            return None

    def solve(self, time_limit=None, target_work_copy=None, solver=GUROBI_NAME, threads=None):
        """
        Generates a schedule from the TTModel
        The solver stops either when the best schedule is obtained or timeLimit
        is reached.

        If stabilize_work_copy is None: does not move the scheduled courses
        whose year group is not in train_prog and fetches from the remote database
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

        print("Optimization started at", \
              datetime.datetime.today().strftime('%Hh%M'))
        result = self.optimize(time_limit, solver, threads=threads)
        print("Optimization ended at", \
              datetime.datetime.today().strftime('%Hh%M'))

        if result is not None:

            if target_work_copy is None:
                target_work_copy = self.choose_free_work_copy()

            self.add_tt_to_db(target_work_copy)
            # for week in self.weeks:
                # reassign_rooms(self.department, week, self.year, target_work_copy)
            print("Added work copy N°%g" % target_work_copy)
            return target_work_copy

    def find_same_course_slot_in_other_week(self, slot, week):
        other_slots = slots_filter(self.wdb.courses_slots, week=week, same=slot)
        if len(other_slots) != 1:
            raise Exception(f"Wrong slots among weeks {week}, {slot.day.week} \n {slot} vs {other_slots}")
        return other_slots.pop()


def get_constraints(department, week=None, year=None, train_prog=None, is_active=None):
    #
    #  Return constraints corresponding to the specific filters
    #
    query = Q(department=department)

    if is_active:
        query &= Q(is_active=is_active)

    if week and not year:
        logger.warning(f"Unable to filter constraint for weeks {week} without specifing year")
        return
    elif train_prog:
        query &= \
            Q(train_progs__abbrev=train_prog) & Q(week__isnull=True) & Q(year__isnull=True) | \
            Q(train_progs__abbrev=train_prog) & Q(week=week) & Q(year=year) | \
            Q(train_progs__isnull=True) & Q(week=week) & Q(year=year) | \
            Q(train_progs__isnull=True) & Q(week__isnull=True) & Q(year__isnull=True)
    else:
        query &= Q(week=week) & Q(year=year) | Q(week__isnull=True) & Q(year__isnull=True)

    # Look up the TTConstraint subclasses records to update
    from TTapp.TTConstraint import TTConstraint, all_subclasses
    types = all_subclasses(TTConstraint)
    for t in types:
        queryset = t.objects.filter(query)

        # Get prefetch  attributes list for the current type
        atributes = t.get_viewmodel_prefetch_attributes()
        if atributes:
            queryset = queryset.prefetch_related(*atributes)

        for constraint in queryset.order_by('id'):
            yield constraint
