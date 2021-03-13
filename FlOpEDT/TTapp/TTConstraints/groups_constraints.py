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

from django.db import models
from django.contrib.postgres.fields import ArrayField
from base.timing import Day

from TTapp.helpers.minhalfdays import MinHalfDaysHelperGroup

from TTapp.slots import slots_filter
from TTapp.TTConstraint import TTConstraint
from people.models import GroupPreferences

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint


def considered_basic_groups(group_ttconstraint, ttmodel):
    if group_ttconstraint.train_progs.exists():
        ttmodel_basic_groups = set(ttmodel.wdb.basic_groups.filter(train_prog__in=group_ttconstraint.train_progs.all()))
    else:
        ttmodel_basic_groups = set(ttmodel.wdb.basic_groups)
    if group_ttconstraint.groups.exists():
        basic_groups = set()
        for g in group_ttconstraint.groups.all():
            basic_groups |= g.basic_groups()
        ttmodel_basic_groups &= basic_groups
    basic_groups_to_consider = set()
    for g in ttmodel_basic_groups:
        if ttmodel.wdb.courses_for_basic_group[g]:
            basic_groups_to_consider.add(g)
    return basic_groups_to_consider


class MinGroupsHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    """
    groups = models.ManyToManyField('base.Group', blank=True)

    def enrich_model(self, ttmodel, week, ponderation=1):
        helper = MinHalfDaysHelperGroup(ttmodel, self, week, ponderation)
        for group in considered_basic_groups(self, ttmodel):
            helper.enrich_model(group=group)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.groups.exists():
            details.update({'groups': ', '.join([group.name for group in self.groups.all()])})

        return view_model

    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.groups.exists():
            text += ' des groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " de tous les groupes"

        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."

        return text


class MinNonPreferedTrainProgsSlot(TTConstraint):
    """
    Minimize the use of unprefered Slots for groups
    """
    def enrich_model(self, ttmodel, week, ponderation=None):
        if ponderation is None:
            ponderation = ttmodel.min_ups_c
        if self.train_progs.exists():
            train_progs = set(tp for tp in self.train_progs.all() if tp in ttmodel.train_prog)
        else:
            train_progs = set(ttmodel.train_prog)
        for train_prog in train_progs:
            basic_groups = ttmodel.wdb.basic_groups.filter(train_prog=train_prog)
            for g in basic_groups:
                g_pref, created = GroupPreferences.objects.get_or_create(group=g)
                g_pref.calculate_fields()
                morning_weight = 2 * g_pref.get_morning_weight()
                evening_weight = 2 * g_pref.get_evening_weight()
                light_day_weight = 2 * g_pref.get_light_day_weight()
                for sl in ttmodel.wdb.availability_slots:
                    day_time_ponderation = light_day_weight
                    if sl in ttmodel.wdb.first_hour_slots:
                        day_time_ponderation *= morning_weight
                    elif sl in ttmodel.wdb.last_hour_slots:
                        day_time_ponderation *= evening_weight

                    for c in ttmodel.wdb.courses_for_basic_group[g]:
                        slot_vars_sum = ttmodel.sum(ttmodel.TT[(sl2, c)]
                                                    for sl2 in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                                            simultaneous_to=sl))
                        cost = self.local_weight() * ponderation * slot_vars_sum \
                            * ttmodel.unp_slot_cost_course[c.type,
                                                           train_prog][sl]
                        cost *= day_time_ponderation
                        ttmodel.add_to_group_cost(g, cost, week=week)

    def one_line_description(self):
        text = "Respecte les préférences"
        if self.train_progs.exists():
            text += ' des groupes de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += ' de toutes les promos.'
        return text


class NoCourseOnDay(TTConstraint):
    FULL_DAY = 'fd'
    AM = 'AM'
    PM = 'PM'
    PERIOD_CHOICES = ((FULL_DAY, 'Full day'), (AM, 'AM'), (PM, 'PM'))
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)
    course_types = models.ManyToManyField('base.CourseType', blank=True, related_name='no_course_on_days')
    groups = models.ManyToManyField('base.Group', blank=True)
    weekday = models.CharField(max_length=2, choices=Day.CHOICES)

    def enrich_model(self, ttmodel, week, ponderation=1):
        considered_courses = set(c for g in considered_basic_groups(self, ttmodel)
                                 for c in ttmodel.wdb.courses_for_basic_group[g])
        if self.course_types.exists():
            considered_courses = set(c for c in considered_courses
                                     if c.type in self.course_types.all())
        if self.period == self.FULL_DAY:
            considered_slots = slots_filter(ttmodel.wdb.courses_slots,
                                            week_day=self.weekday, week=week)
        else:
            considered_slots = slots_filter(ttmodel.wdb.courses_slots,
                                            week_day=self.weekday, apm=self.period, week=week)
        considered_sum = ttmodel.sum(ttmodel.TT[(sl, c)]
                                     for c in considered_courses
                                     for sl in considered_slots & ttmodel.wdb.compatible_slots[c])
        if self.weight is None:
            ttmodel.add_constraint(considered_sum,
                                   '==', 0,
                                   Constraint(constraint_type=ConstraintType.NO_COURSE_ON_DAY, weeks=week))
        else:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * considered_sum, week)

    def one_line_description(self):
        text = f"Aucun cours le {self.weekday}"
        if self.period != self.FULL_DAY:
            text += f" ({self.period})"
        if self.course_types.exists():
            text += f" pour les cours de type" + ', '.join([t.name for t in self.course_types.all()])
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        return text