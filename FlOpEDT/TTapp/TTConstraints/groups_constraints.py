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
from base.models import StructuralGroup
from TTapp.helpers.minhalfdays import MinHalfDaysHelperGroup
from base.timing import Day
from TTapp.slots import slots_filter, days_filter
from TTapp.TTConstraints.TTConstraint import TTConstraint
from people.models import GroupPreferences
from django.contrib.postgres.fields import ArrayField


from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint

from django.utils.translation import gettext_lazy as _

import datetime as dt

def pre_analysis_considered_basic_groups(group_ttconstraint):
    
    """
    Returns a set of groups which are basic_group concerned by the constraint group_ttconstraint

    :param group_ttconstraint: A constraint we want to analyze.
    :type group_ttconstraint: TTConstraint
    :return: A set of groups which are basic_group and concerned by the constraint.
    :rtype: A set of StructuralGroup

    """
    
    groups = set(StructuralGroup.objects.filter(train_prog__in=group_ttconstraint.train_progs.all()))
    basic_groups = set()
    
    for g in groups :
        if len(g.descendants_groups()) == 0 :
            basic_groups.add(g)
    
    if group_ttconstraint.groups.exists():
        
        basic_groups_constraint = set()
        
        for g in group_ttconstraint.groups.all():
            
            basic_groups_constraint.add(g)
        
        basic_groups &= basic_groups_constraint
        
    return basic_groups

'''
    basic_groups_to_consider = set()
    for g in basic_groups:
        if ttmodel.wdb.courses_for_basic_group[g]:
            basic_groups_to_consider.add(g)
'''


def considered_basic_groups(group_ttconstraint, ttmodel=None):
    if ttmodel is None:
        basic_groups = StructuralGroup.objects.filter(train_prog__department=group_ttconstraint.department,
                                                      basic=True)
    else:
        basic_groups = ttmodel.wdb.basic_groups
    if group_ttconstraint.train_progs.exists():
        basic_groups = set(basic_groups.filter(train_prog__in=group_ttconstraint.train_progs.all()))
    else:
        basic_groups = set(basic_groups)
    if group_ttconstraint.groups.exists():
        constraint_basic_groups = set()
        for g in group_ttconstraint.groups.all():
            constraint_basic_groups |= g.basic_groups()
        basic_groups &= constraint_basic_groups
    if ttmodel is None:
        return basic_groups
    else:
        ttmodel_basic_groups_to_consider = set()
        for g in basic_groups:
            if ttmodel.wdb.courses_for_basic_group[g]:
                ttmodel_basic_groups_to_consider.add(g)
        return ttmodel_basic_groups_to_consider


class MinGroupsHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    """
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)

    class Meta:
        verbose_name = _('Minimize busy half-days for groups')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        helper = MinHalfDaysHelperGroup(ttmodel, self, period, ponderation)
        for group in self.considered_basic_groups(ttmodel):
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

    def __str__(self):
        return _("Minimize groups half-days")


class MinNonPreferedTrainProgsSlot(TTConstraint):
    """
    Minimize the use of unprefered Slots for groups.
    Make impossible the use of forbidden slots.
    """
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)
    
    class Meta:
        verbose_name = _('Minimize undesired slots for groups')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=None):
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
                        cost *= (day_time_ponderation + 1)
                        ttmodel.add_to_group_cost(g, cost, period=period)

            if self.weight is None:
                for course_type in ttmodel.wdb.course_types:
                    for sl in ttmodel.wdb.availability_slots:
                        if ttmodel.avail_course[(course_type, train_prog)][sl] == 0:
                            ttmodel.add_constraint(
                                ttmodel.sum(ttmodel.TT[(sl2, c)]
                                            for g in basic_groups
                                            for c in ttmodel.wdb.courses_for_basic_group[g]
                                            for sl2 in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                                    simultaneous_to=sl)),
                                '==',
                                0,
                                Constraint(constraint_type=ConstraintType.TRAIN_PROG_FORBIDDEN_SLOT,
                                           slots=sl)
                            )


    def one_line_description(self):
        text = "Respecte les préférences"
        if self.train_progs.exists():
            text += ' des groupes de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += ' de toutes les promos.'
        return text

    def __str__(self):
        return _("Minimize groups non-preferred slots")


class GroupsMinHoursPerDay(TTConstraint):
    """
    Respect the min_time_per_day declared
    """
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)
    min_time = models.DurationField(default=dt.timedelta(hours=3), verbose_name=_('min_time'))
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)

    class Meta:
        verbose_name = _('Respect groups min time per day bounds')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        """
        avoid situations in which a teaching day has less hours than time
        """
        considered_groups = self.considered_basic_groups(ttmodel)

        min_time = self.min_time
        if not min_time:
            return

        days = days_filter(ttmodel.wdb.days, period=period)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        for basic_group in considered_groups:
            for day in days:
                group_day_scheduled_minutes = ttmodel.sum(ttmodel.TT[sl, c] * sl.minutes
                                             for c in ttmodel.wdb.courses_for_basic_group[basic_group]
                                             for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day=day))
                has_enough_time = ttmodel.add_floor(group_day_scheduled_minutes,
                                                    min_time.seconds//60,
                                                    100000)
                undesired_situation = ttmodel.GBD[(basic_group, day)] - has_enough_time
                if self.weight is None:
                    ttmodel.add_constraint(undesired_situation,
                                           '==',
                                           0,
                                           Constraint(constraint_type=ConstraintType.MIN_HOURS_PER_DAY,
                                                      groups=basic_group,
                                                      days=day))
                else:
                    ttmodel.add_to_group_cost(basic_group, self.local_weight() * ponderation * undesired_situation,
                                              period=period)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.groups.exists():
            details.update({'groups': ', '.join([group.full_name for group in self.groups.all()])})
        else:
            details.update({'groups': 'All'})
        return view_model

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "Groups min hours per day"
