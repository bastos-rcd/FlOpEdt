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
import logging

from base.models import Time, TimeGeneralSettings
from people.models import GroupPreferences
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.slots import days_filter, slots_filter

logger = logging.Logger(__name__)


class MinHalfDaysHelperBase():

    def __init__(self, ttmodel, constraint, period, ponderation):
        self.ttmodel = ttmodel
        self.constraint = constraint
        self.ponderation = ponderation
        self.period = period

    def build_variables(self):
        return None, None

    def add_cost(self, cost):
        pass

    def minimal_half_days_number(self, courses):
        """
        Ce code (pas encore idéal) remplace le code suivant
            course_time = sum(c.duration for c in courses)
            limit = (course_time - 1) // half_days_min_time + 1
        qui avait le défaut que :
        si par exemple la demie-journée fait 4h30 et qu'on a 3 cours de 3h (soit 9h en tout) ça impose de le faire tenir
        en 2 demies-journées... impossible !
        """
        t = TimeGeneralSettings.objects.get(department=self.ttmodel.department)
        today = dt.date.today()
        half_days_min_time = min(dt.datetime.combine(today, t.morning_end_time)-dt.datetime.combine(today, t.day_start_time),
                                 dt.datetime.combine(today, t.day_end_time)-dt.datetime.combine(today, t.afternoon_start_time))
        considered_courses = list(courses)
        considered_courses.sort(key=lambda x: x.duration)
        limit = 0
        while considered_courses:
            c = considered_courses.pop()
            d = c.duration
            for c2 in considered_courses[-1::-1]:
                if d + c2.duration <= half_days_min_time:
                    d += c2.duration
                    considered_courses.remove(c2)
            limit+=1
        return limit

    def add_constraint(self, expression, courses):
        limit = self.minimal_half_days_number(courses)
        half_days = {i: self.ttmodel.add_floor(expression, i, 100)
                     for i in range(2, 2 * len(self.ttmodel.data.days) + 1)}
        if self.constraint.weight is None:
            if limit + 1 in half_days:
                self.ttmodel.add_constraint(half_days[limit + 1], '==', 0,
                                            Constraint(constraint_type=ConstraintType.MIN_HALF_DAYS_LIMIT))
        cost = self.ttmodel.lin_expr()
        for i in half_days:
            cost += self.constraint.local_weight() * self.ponderation * half_days[i]
        self.add_cost(cost)

    def enrich_model(self, **args):
        expression, courses = self.build_variables()
        self.add_constraint(expression, courses)


class MinHalfDaysHelperModule(MinHalfDaysHelperBase):

    def build_variables(self):
        days = days_filter(self.ttmodel.data.days, period=self.period)
        mod_b_h_d = {}
        for d in days:
            mod_b_h_d[(self.module, d, Time.AM)] \
                = self.ttmodel.add_var("ModBHD(%s,%s,%s)"
                                    % (self.module, d, Time.AM))
            mod_b_h_d[(self.module, d, Time.PM)] \
                = self.ttmodel.add_var("ModBHD(%s,%s,%s)"
                                    % (self.module, d, Time.PM))

            # add constraint linking MBHD to TT
            for apm in [Time.AM, Time.PM]:
                halfdayslots = set(sl for sl in self.ttmodel.data.courses_slots if sl.day == d and sl.apm == apm)
                card = len(halfdayslots)
                expr = self.ttmodel.lin_expr()
                expr += card * mod_b_h_d[(self.module, d, apm)]
                for sl in halfdayslots:
                    for c in set(self.ttmodel.data.courses.filter(module=self.module))\
                            & self.ttmodel.data.compatible_courses[sl]:
                        expr -= self.ttmodel.scheduled[(sl, c)]
                self.ttmodel.add_constraint(expr, '>=', 0,
                                            Constraint(constraint_type=ConstraintType.MIN_HALF_DAYS_SUP))
                self.ttmodel.add_constraint(expr, '<=', card - 1,
                                            Constraint(constraint_type=ConstraintType.MIN_HALF_DAYS_INF))

        courses = self.ttmodel.data.courses.filter(module=self.module, period=self.period)
        expression = self.ttmodel.sum(
            mod_b_h_d[(self.module, d, apm)]
            for d in days
            for apm in [Time.AM, Time.PM])

        return expression, courses

    def add_cost(self, cost):
        self.ttmodel.add_to_generic_cost(cost)

    def enrich_model(self, module=None):
        if module:
            self.module = module
            super().enrich_model()
        else:
            raise "MinHalfDaysHelperModule requires a module argument"


class MinHalfDaysHelperGroup(MinHalfDaysHelperBase):

    def build_variables(self):
        courses = set(c for c in self.ttmodel.data.all_courses_for_basic_group[self.group]
                      if c.period == self.period)

        expression = self.ttmodel.sum(self.ttmodel.GBHD[self.group, d, apm] for apm in self.ttmodel.possible_apms
             for d in self.ttmodel.data.days if d in self.period.dates())

        return expression, courses

    def add_cost(self, cost):
        g_pref, created = GroupPreferences.objects.get_or_create(group = self.group)
        g_pref.calculate_fields()
        free_half_day_weight = g_pref.get_free_half_day_weight()
        self.ttmodel.add_to_group_cost(self.group, free_half_day_weight * cost, self.period)

    def enrich_model(self, group=None):
        if group:
            self.group = group
            super().enrich_model()
        else:
            raise Exception("MinHalfDaysHelperGroup requires a group argument")


class MinHalfDaysHelperTutor(MinHalfDaysHelperBase):

    def build_variables(self):
        courses = set(c for c in self.ttmodel.data.possible_courses[self.tutor] if c.period == self.period)
        days = days_filter(self.ttmodel.data.days, period=self.period)
        expression = self.ttmodel.sum(
            self.ttmodel.IBHD[(self.tutor, d, apm)]
            for d in days
            for apm in [Time.AM, Time.PM])

        return expression, courses

    def add_cost(self, cost):
        self.ttmodel.add_to_inst_cost(self.tutor, cost, self.period)

    def add_constraint(self, expression, courses):
        super().add_constraint(expression, courses)
        days = days_filter(self.ttmodel.data.days, period=self.period)
        # Try to joincourses
        if self.constraint.join2courses and len(courses) in [2, 4]:
            for d in days:
                for c in courses:
                    sl8h = min(slots_filter(self.ttmodel.data.courses_slots, day=d, apm=Time.AM) & self.ttmodel.data.compatible_slots[c])
                    sl14h = min(slots_filter(self.ttmodel.data.courses_slots, day=d, apm=Time.PM) & self.ttmodel.data.compatible_slots[c])
                    for c2 in courses - {c}:
                        sl11h = max(
                            slots_filter(self.ttmodel.data.courses_slots, day=d, apm=Time.AM) & self.ttmodel.data.compatible_slots[c2])
                        sl17h = max(
                            slots_filter(self.ttmodel.data.courses_slots, day=d, apm=Time.PM) & self.ttmodel.data.compatible_slots[c2])
                        if self.constraint.weight:
                            conj_var_AM = self.ttmodel.add_conjunct(self.ttmodel.scheduled[(sl8h, c)],
                                                                    self.ttmodel.scheduled[(sl11h, c2)])
                            conj_var_PM = self.ttmodel.add_conjunct(self.ttmodel.scheduled[(sl14h, c)],
                                                                    self.ttmodel.scheduled[(sl17h, c2)])
                            self.ttmodel.add_to_inst_cost(self.tutor,
                                                          self.constraint.local_weight() * self.ponderation *
                                                          (conj_var_AM + conj_var_PM)/2,
                                                          period=self.period)
                        else:
                            self.ttmodel.add_constraint(
                                self.ttmodel.scheduled[(sl8h, c)] + self.ttmodel.scheduled[(sl11h, c2)],
                                '<=',
                                1,
                                Constraint(constraint_type=ConstraintType.MIN_HALF_DAYS_JOIN_AM))
                            self.ttmodel.add_constraint(
                                self.ttmodel.scheduled[(sl14h, c)] + self.ttmodel.scheduled[(sl17h, c2)],
                                '<=',
                                1, Constraint(constraint_type=ConstraintType.MIN_HALF_DAYS_JOIN_PM))

    def enrich_model(self, tutor=None):
        if tutor:
            self.tutor = tutor
            super().enrich_model()
        else:
            raise Exception("MinHalfDaysHelperTutor requires a tutor argument")
