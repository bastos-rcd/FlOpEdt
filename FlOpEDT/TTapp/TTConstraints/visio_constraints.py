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

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.TTConstraints.groups_constraints import considered_basic_groups
from base.timing import Day, Time, min_to_str
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class NoVisio(TTConstraint):
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True, related_name='no_visio')
    course_types = models.ManyToManyField('base.CourseType', blank=True, related_name='no_visio')
    modules = models.ManyToManyField('base.Module', blank=True, related_name='no_visio')

    class Meta:
        verbose_name = _('No visio courses')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1000000):
        if not self.department.mode.visio:
            print("Visio Mode is not activated : ignore NoVisio constraint")
            return
        considered_groups = considered_basic_groups(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, week=week)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        for group in considered_groups:
            # Si contrainte forte, AUCUN cours en visio
            # Sinon un poids LOURD pour chaque cours mis en Visio (sauf ceux indiqués Visio!)
            if self.weight is None:
                considered_group_courses = ttmodel.wdb.courses_for_basic_group[group]
            else:
                considered_group_courses = ttmodel.wdb.courses_for_basic_group[group] \
                                                  - ttmodel.wdb.visio_courses

            if self.course_types.exists():
                considered_group_courses = set(c for c in considered_group_courses
                                               if c.type in self.course_types.all())
            if self.modules.exists():
                considered_group_courses = set(c for c in considered_group_courses
                                               if c.module in self.modules.all())
            relevant_sum = ttmodel.sum(ttmodel.TTrooms[sl, c, None]
                                       for c in considered_group_courses
                                       for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day_in=days))
            if self.weight is None:
                ttmodel.add_constraint(relevant_sum,
                                       '==',
                                       0,
                                       Constraint(constraint_type=ConstraintType.NO_VISIO, groups=group))
            else:
                ttmodel.add_to_group_cost(group, self.local_weight() * ponderation * relevant_sum)

    def one_line_description(self):
        text = "Pas de visio"
        if self.weight is not None:
            " (sauf demande expresse)"
        if self.weekdays:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        if self.course_types.exists():
            text += ' pour les cours de type ' + ', '.join([t.name for t in self.course_types.all()])
        if self.modules.exists():
            text += ' en ' + ', '.join([module.abbrev for module in self.modules.all()])
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text


class VisioOnly(TTConstraint):
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True, related_name='visio_only')
    course_types = models.ManyToManyField('base.CourseType', blank=True, related_name='visio_only')
    modules = models.ManyToManyField('base.Module', blank=True, related_name='visio_only')

    class Meta:
        verbose_name = _('Only visio courses')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1000000):
        if not self.department.mode.visio:
            print("Visio Mode is not activated : ignore VisioOnly constraint")
            return
        considered_groups = considered_basic_groups(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, week=week)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        for group in considered_groups:
            # Si contrainte forte, Tous les cours en visio,
            # Sinon un poids LOURD pour chaque cours mis en Présentiel (sauf ceux indiqués no Visio!)
            if self.weight is None:
                considered_group_courses = ttmodel.wdb.courses_for_basic_group[group]
            else:
                considered_group_courses = ttmodel.wdb.courses_for_basic_group[group] \
                                           - ttmodel.wdb.no_visio_courses
            if self.course_types.exists():
                considered_group_courses = set(c for c in considered_group_courses
                                               if c.type in self.course_types.all())
            if self.modules.exists():
                considered_group_courses = set(c for c in considered_group_courses
                                               if c.module in self.modules.all())
            relevant_sum = ttmodel.sum(ttmodel.TTrooms[sl, c, r]
                                       for c in considered_group_courses
                                       for r in ttmodel.wdb.course_rg_compat[c] - {None}
                                       for sl in slots_filter(ttmodel.wdb.compatible_slots[c], day_in=days))
            if self.weight is None:
                ttmodel.add_constraint(relevant_sum,
                                       '==',
                                       0,
                                       Constraint(constraint_type=ConstraintType.VISIO_ONLY, groups=group))
            else:
                ttmodel.add_to_group_cost(group, self.local_weight() * ponderation * relevant_sum)


    def one_line_description(self):
        text = "Tout en visio"
        if self.weight is not None:
            " (sauf demande expresse)"
        if self.weekdays:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        if self.course_types.exists():
            text += ' pour les cours de type ' + ', '.join([t.name for t in self.course_types.all()])
        if self.modules.exists():
            text += ' en ' + ', '.join([module.abbrev for module in self.modules.all()])
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text


class LimitGroupsPhysicalPresence(TTConstraint):
    """
    at most a given proportion of basic groups are present each half-day
    """
    percentage = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)

    class Meta:
        verbose_name = _('Limit simultaneous physical presence')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1000):
        if not self.department.mode.visio:
            print("Visio Mode is not activated : ignore LimitGroupsPhysicalPresence constraint")
            return
        if self.train_progs.exists():
            considered_basic_groups = set(
                ttmodel.wdb.basic_groups.filter(train_prog__in=self.train_progs.all()))
        else:
            considered_basic_groups = set(ttmodel.wdb.basic_groups)
        days = days_filter(ttmodel.wdb.days, week=week)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        proportion = self.percentage / 100
        nb_of_basic_groups = len(considered_basic_groups)
        for d in days:
            for apm in [Time.AM, Time.PM]:
                physically_presents_groups_number = ttmodel.sum(ttmodel.physical_presence[g][d, apm]
                                                                for g in ttmodel.wdb.basic_groups)
                is_over_bound = ttmodel.add_floor(physically_presents_groups_number,
                                                  nb_of_basic_groups * proportion + 1,
                                                  2 * nb_of_basic_groups)
                if self.weight is None:
                    ttmodel.add_constraint(
                        is_over_bound,
                        '==', 0,
                        Constraint(constraint_type=ConstraintType.VISIO_LIMIT_GROUP_PRESENCE))
                else:
                    ttmodel.add_to_generic_cost(is_over_bound * self.local_weight() * ponderation, week=week)

    def one_line_description(self):
        text = "Pas plus de " + str(self.percentage) + "% des groupes"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += ", toutes promos confondues,"
        text += "sont physiquement présents chaque demie-journée"
        if self.weekdays:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        return text


class BoundPhysicalPresenceHalfDays(TTConstraint):
    """
    Bound the number of Half-Days of physical presence
    """
    nb_max = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(14)], default=14)
    nb_min = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(14)], default=0)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True, related_name='bound_physical_presence_half_days')

    class Meta:
        verbose_name = _('Bound physical presence half days')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        if not self.department.mode.visio:
            print("Visio Mode is not activated : ignore BoundPhysicalPresenceHalfDays constraint")
            return
        considered_groups = considered_basic_groups(self, ttmodel)
        total_nb_half_days = len(ttmodel.wdb.days) * 2
        physical_presence_half_days_number = {}
        for g in considered_groups:
            physical_presence_half_days_number[g] = \
                ttmodel.sum(ttmodel.physical_presence[g][d, apm]
                            for (d, apm) in ttmodel.physical_presence[g])
        if self.weight is None:
            for g in considered_groups:
                # at least nb_min half-days of physical-presence for each group
                ttmodel.add_constraint(
                    physical_presence_half_days_number[g], '>=', self.nb_min,
                    Constraint(constraint_type=ConstraintType.MIN_PHYSICAL_HALF_DAYS, groups=g, weeks=week))

                # at most nb_max half-days of physical presence for each group
                ttmodel.add_constraint(physical_presence_half_days_number[g], '<=', self.nb_max,
                                       Constraint(constraint_type=ConstraintType.MAX_PHYSICAL_HALF_DAYS,
                                                  groups=g, weeks=week))
        else:
            for g in considered_groups:
                cost = ponderation * self.local_weight() * \
                       (ttmodel.one_var - ttmodel.add_floor(physical_presence_half_days_number[g],
                                                       self.nb_min, total_nb_half_days)
                        + ttmodel.add_floor(physical_presence_half_days_number[g],
                                            self.nb_max, total_nb_half_days))
                ttmodel.add_to_group_cost(g, cost, week)

    def one_line_description(self):
        text = f"Au moins {self.nb_min} et au plus {self.nb_max} demie_journées de présentiel"
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour chaque groupe"
        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text


class Curfew(TTConstraint):
    """
        Defines a curfew (after which only Visio courses are allowed)
    """
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    curfew_time = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24*60)])

    class Meta:
        verbose_name = _('Curfew')
        verbose_name_plural = verbose_name

    def one_line_description(self):
        text = f"Curfew after {min_to_str(self.curfew_time)}"

    def enrich_ttmodel(self, ttmodel, week, ponderation=2):
        if not self.department.mode.visio:
            print("Visio Mode is not activated : ignore Curfew constraint")
            return
        days = days_filter(ttmodel.wdb.days, week=week)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)

        relevant_sum = ttmodel.sum(ttmodel.TTrooms[sl, c, r]
                                   for c in ttmodel.wdb.courses
                                   for r in ttmodel.wdb.course_rg_compat[c] - {None}
                                   for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                          ends_after=self.curfew_time,
                                                          day_in=days,
                                                          week=week))
        if self.weight is None:
            ttmodel.add_constraint(relevant_sum,
                                   '==',
                                   0,
                                   Constraint(constraint_type=ConstraintType.CURFEW))
        else:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * relevant_sum)
