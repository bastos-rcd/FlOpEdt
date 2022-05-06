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
import os, fnmatch

from pulp import LpVariable, LpConstraint, LpBinary, LpConstraintEQ, \
    LpConstraintGE, LpConstraintLE, LpAffineExpression, LpProblem, LpStatus, \
    LpMinimize, lpSum, LpStatusOptimal, LpStatusNotSolved
import pulp
from pulp import GUROBI_CMD
import signal
import logging
from TTapp.ilp_constraints.constraintManager import ConstraintManager
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from base.models import Department, ScheduledCourse

from core.decorators import timer
from django.db import close_old_connections
from django.db.models import Q, Max

from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.RoomConstraints.RoomConstraint import RoomConstraint
from TTapp.FlopConstraint import all_subclasses

logger = logging.getLogger(__name__)
pattern = r".+: (.|\s)+ (=|>=|<=) \d*"
GUROBI = 'GUROBI'
GUROBI_NAME = 'GUROBI_CMD'
solution_files_path = "misc/logs/solutions"


class FlopModel(object):
    def __init__(self, department_abbrev, weeks, keep_many_solution_files=False):
        self.department = Department.objects.get(abbrev=department_abbrev)
        self.weeks = weeks
        self.model = LpProblem(self.solution_files_prefix(), LpMinimize)
        self.keep_many_solution_files = keep_many_solution_files
        self.var_nb = 0
        self.constraintManager = ConstraintManager()
        self.one_var = self.add_var()
        self.add_constraint(self.one_var, '==', 1, Constraint(constraint_type=ConstraintType.TECHNICAL))
        self.warnings = {}
        self.obj = self.lin_expr()

    def add_var(self, name=""):
        """
        Create a PuLP binary variable
        """
        self.var_nb += 1
        return LpVariable(str(self.var_nb), cat=LpBinary)

    def add_constraint(self, expr, relation, value, constraint=Constraint()):
        """
        Add a mathematical (in)equation to the system
        """
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

    @staticmethod
    def lin_expr(expr=None):
        return LpAffineExpression(expr)

    @staticmethod
    def sum(*args):
        return lpSum(list(*args))

    @staticmethod
    def get_var_value(ttvar):
        return round(ttvar.value())

    @staticmethod
    def get_expr_value(ttexpr):
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
        Create a new var that is the conjunction of v1 and v2 and add it to the model
        """
        l_conj_var = self.add_var()
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
                            Constraint(constraint_type=ConstraintType.FLOOR_BOUND))
        self.add_constraint(l_floor * bound - expr, '>=', 1 - floor,
                            Constraint(constraint_type=ConstraintType.CEILING_BOUND))
        return l_floor

    def add_if_var_a_then_not_vars_b_constraint(self, var_a, vars_b_list):
        bound = len(vars_b_list) + 1
        self.add_constraint(bound * var_a + self.sum(var for var in vars_b_list), '<=', bound,
                            Constraint(constraint_type=ConstraintType.SI_A_ALORS_NON_B))

    def add_warning(self, key, warning):
        if key in self.warnings:
            self.warnings[key].append(warning)
        else:
            self.warnings[key] = [warning]

    def solution_files_prefix(self):
        raise NotImplementedError

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

    def choose_free_work_copy(self):
        close_old_connections()

        local_max_wc = ScheduledCourse \
            .objects \
            .filter(course__module__train_prog__department=self.department,
                    course__week__in=self.weeks) \
            .aggregate(Max('work_copy'))['work_copy__max']

        if local_max_wc is None:
            local_max_wc = -1

        return local_max_wc + 1

    def write_infaisability(self, write_iis=True, write_analysis=True, presolve=False):
        close_old_connections()
        file_path = "misc/logs/iis"
        filename_suffixe = "_%s_%s" % (self.department.abbrev, self.weeks)
        iis_filename = "%s/IIS%s.ilp" % (file_path, filename_suffixe)
        if write_iis:
            from gurobipy import read, GurobiError
            lp = f"{self.solution_files_prefix()}-pulp.lp"
            m = read(lp)
            if presolve:
                try:
                    mp = m.presolve()
                    mp.computeIIS()
                    mp.write(iis_filename)
                except GurobiError:
                    m.computeIIS()
                    m.write(iis_filename)
            else:
                m.computeIIS()
                m.write(iis_filename)
        if write_analysis:
            self.constraintManager.handle_reduced_result(iis_filename, file_path, filename_suffixe)

    @timer
    def optimize(self, time_limit, solver, presolve=2, threads=None, ignore_sigint=True):
        # The solver value shall be one of the available
        # solver corresponding pulp command or contain
        # gurobi
        if 'gurobi' in solver.lower() and hasattr(pulp, GUROBI_NAME):
            self.delete_solution_files(all=True)
            if ignore_sigint:
                # ignore SIGINT while solver is running
                # => SIGINT is still delivered to the solver, which is what we want
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
            # print(f'lpfile has been saved in {self.solution_files_prefix()}-pulp.lp')
            return None


def get_ttconstraints(department, week=None, train_prog=None, is_active=None):
    #
    #  Return constraints corresponding to the specific filters
    #
    query = Q(department=department)

    if is_active:
        query &= Q(is_active=is_active)

    if train_prog:
        query &= \
            Q(train_progs__abbrev=train_prog) & Q(weeks__isnull=True) | \
            Q(train_progs__abbrev=train_prog) & Q(weeks=week) | \
            Q(train_progs__isnull=True) & Q(weeks=week) | \
            Q(train_progs__isnull=True) & Q(weeks__isnull=True)
    else:
        query &= Q(weeks=week) | Q(weeks__isnull=True)

    # Look up the TTConstraint subclasses records to update
    types = all_subclasses(TTConstraint)
    for t in types:
        queryset = t.objects.filter(query)

        # Get prefetch  attributes list for the current type
        atributes = t.get_viewmodel_prefetch_attributes()
        if atributes:
            queryset = queryset.prefetch_related(*atributes)

        for constraint in queryset.order_by('id'):
            yield constraint


def get_room_constraints(department, week=None, is_active=None):
    #
    #  Return constraints corresponding to the specific filters
    #
    query = Q(department=department)

    if is_active:
        query &= Q(is_active=is_active)

    query &= Q(weeks=week) | Q(weeks__isnull=True)

    # Look up the TTConstraint subclasses records to update
    types = all_subclasses(RoomConstraint)
    for t in types:
        queryset = t.objects.filter(query)

        # Get prefetch  attributes list for the current type
        atributes = t.get_viewmodel_prefetch_attributes()
        if atributes:
            queryset = queryset.prefetch_related(*atributes)

        for constraint in queryset.order_by('id'):
            yield constraint