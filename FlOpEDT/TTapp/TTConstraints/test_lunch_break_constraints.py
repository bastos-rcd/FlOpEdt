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


from django.contrib.postgres.fields import ArrayField

from django.db import models

from django.core.exceptions import ObjectDoesNotExist

from base.timing import french_format
from base.timing import Day

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import days_filter, slots_filter
from TTapp.TTConstraint import TTConstraint
from TTapp.TTConstraints.groups_constraints import considered_basic_groups
from TTapp.slots import Slot

class LunchBreak(TTConstraint):
    """
    Abstract class Ensures time for lunch in a given interval
    """

    start_time = models.PositiveSmallIntegerField()
    end_time = models.PositiveSmallIntegerField()
    weekdays = ArrayField(models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True)
    lunch_length = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True

    def considered_days(self, ttmodel, week):
        days = days_filter(ttmodel.wdb.days, week=week)
        if self.weekdays:
            days = days_filter(days, day_in=self.weekdays)
        return days

    def day_lunch_slots(self, day):
        return [Slot(day=day, start_time=st, end_time=st+self.lunch_length)
                for st in range(self.start_time, self.end_time - self.lunch_length + 1, 15)]

    def build_day_expression(self, ttmodel, day, considered_courses, tutor=None):
        expr = ttmodel.lin_expr()
        for slot in self.day_lunch_slots(day):
            for course in considered_courses & ttmodel.wdb.compatible_courses[slot]:
                expr += ttmodel.TT[(slot, course)]

        return expr

    def undesired_scheduled_courses_expression(self, ttmodel, week, day, tutor, group):
        raise NotImplementedError

    def considered_courses(self, ttmodel, week, day,  tutor, group):
        return set(self.get_courses_queryset_by_parameters(ttmodel, week, day,
                                                           group=group,
                                                           tutor=tutor))

    def enrich_model_for_one_object(self, ttmodel, week, ponderation,
                                    tutor=None, group=None):
        for day in self.considered_days(ttmodel, week):
            local_slots = self.day_lunch_slots(day)
            slots_nb = len(local_slots)
            # pour chaque groupe, au moins un de ces slots ne voit aucun cours lui être simultané
            slot_vars = {}
            considered_courses = self.considered_courses(ttmodel, week, day, tutor, group)
            for local_slot in local_slots:
                # Je veux que slot_vars[group, local_slot] soit à 1
                # si et seulement si undesired_scheduled_courses vaut plus que 1

                slot_vars[local_slot] = ttmodel.add_floor(
                    expr=self.undesired_scheduled_courses_expression(ttmodel, week, day, tutor, group),
                    bound=len(considered_courses))
            not_ok = ttmodel.add_floor(expr=ttmodel.sum(slot_vars[sl] for sl in local_slots),
                                       floor=slots_nb,
                                       bound=2 * slots_nb)

            if self.weight is None:
                ttmodel.add_constraint(not_ok, '==', 0, Constraint(ConstraintType.LUNCH_BREAK,
                                                                   groups=group))
                # ttmodel.add_constraint(ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                #                        '<=', len(local_slots),
                #                        Constraint(constraint_type=ConstraintType.LUNCH_BREAK,
                #                                   groups=group, days=day))
            else:
                cost = not_ok * ponderation * self.local_weight()
                # cost = ttmodel.sum(slot_vars[group, sl] for sl in local_slots) * ponderation \
                #        * self.local_weight()
                ttmodel.add_to_group_cost(group, cost, week)

class GroupsLunchBreak(LunchBreak):
    """
    Ensures time for lunch in a given interval for given groups (all if groups is Null)
    """
    groups = models.ManyToManyField('base.Group', blank=True, related_name='lunch_breaks_constraints')

    def undesired_scheduled_courses_expression(self, ttmodel, week, day, group, tutor=None):
        ttmodel.sum(ttmodel.TT[sl, c] for c in self.considered_courses(ttmodel, week, day, tutor, group)
                    for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                           simultaneous_to=self.day_lunch_slots(day)))

    def enrich_model(self, ttmodel, week, ponderation=1000000):
        considered_groups = considered_basic_groups(self, ttmodel)

        for day in self.considered_days(ttmodel, week):
            local_slots = self.day_lunch_slots(day)
            slots_nb = len(local_slots)
            # pour chaque groupe, au moins un de ces slots ne voit aucun cours lui être simultané
            slot_vars = {}

            for group in considered_groups:
                considered_courses = self.get_courses_queryset_by_parameters(ttmodel, week, group=group)
                for local_slot in local_slots:
                    # Je veux que slot_vars[group, local_slot] soit à 1
                    # si et seulement si undesired_scheduled_courses vaut plus que 1
                    undesired_scheduled_courses = \
                        ttmodel.sum(ttmodel.TT[sl, c] for c in considered_courses
                                    for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                           simultaneous_to=local_slot))
                    slot_vars[group, local_slot] = ttmodel.add_floor(expr=undesired_scheduled_courses,
                                                                     floor=1,
                                                                     bound=len(considered_courses))
                not_ok = ttmodel.add_floor(expr=ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                                           floor=slots_nb,
                                           bound=2 * slots_nb)

                if self.weight is None:
                    ttmodel.add_constraint(not_ok,'==', 0, Constraint(ConstraintType.LUNCH_BREAK,
                                                                      groups=group))
                    # ttmodel.add_constraint(ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                    #                        '<=', len(local_slots),
                    #                        Constraint(constraint_type=ConstraintType.LUNCH_BREAK,
                    #                                   groups=group, days=day))
                else:
                    cost = not_ok * ponderation * self.local_weight()
                    # cost = ttmodel.sum(slot_vars[group, sl] for sl in local_slots) * ponderation \
                    #        * self.local_weight()
                    ttmodel.add_to_group_cost(group, cost, week)


    def one_line_description(self):
        text = f"Il faut une pause déjeuner d'au moins {self.lunch_length} minutes " \
               f"entre {french_format(self.start_time)} et {french_format(self.end_time)}"
        try:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        except ObjectDoesNotExist:
            pass
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"

        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text


class TutorsLunchBreak(LunchBreak):
    """
    Ensures time for lunch in a given interval for given groups (all if groups is Null)
    """
    tutors = models.ManyToManyField('people.Tutor', blank=True, related_name='lunch_breaks_constraints')

    def undesired_scheduled_courses_expression(self, ttmodel, week, day, tutor, group=None):
        ttmodel.sum(ttmodel.TTinstructors[sl, c, tutor]
                    for c in self.considered_courses(ttmodel, week, day, tutor, group)
                    for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                           simultaneous_to=self.day_lunch_slots(day)))

    def enrich_model(self, ttmodel, week, ponderation=1000000):
        considered_tutors = set(ttmodel.wdb.instructors)
        if self.tutors.exists():
            considered_tutors &= set(self.tutors.all())

        for day in self.considered_days(ttmodel, week):
            local_slots = self.day_lunch_slots(day)
            slots_nb = len(local_slots)
            # pour chaque groupe, au moins un de ces slots ne voit aucun cours lui être simultané
            slot_vars = {}

            for tutor in considered_tutors:
                considered_courses = self.get_courses_queryset_by_parameters(ttmodel, week, tutor=tutor)
                for local_slot in local_slots:
                    # Je veux que slot_vars[group, local_slot] soit à 1
                    # si et seulement si undesired_scheduled_courses vaut plus que 1
                    undesired_scheduled_courses = \
                        ttmodel.sum(ttmodel.TT[sl, c] for c in considered_courses
                                    for sl in slots_filter(ttmodel.wdb.compatible_slots[c],
                                                           simultaneous_to=local_slot))
                    slot_vars[group, local_slot] = ttmodel.add_floor(expr=undesired_scheduled_courses,
                                                                     floor=1,
                                                                     bound=len(considered_courses))
                not_ok = ttmodel.add_floor(expr=ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                                           floor=slots_nb,
                                           bound=2 * slots_nb)

                if self.weight is None:
                    ttmodel.add_constraint(not_ok, '==', 0, Constraint(ConstraintType.LUNCH_BREAK,
                                                                       groups=group))
                    # ttmodel.add_constraint(ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                    #                        '<=', len(local_slots),
                    #                        Constraint(constraint_type=ConstraintType.LUNCH_BREAK,
                    #                                   groups=group, days=day))
                else:
                    cost = not_ok * ponderation * self.local_weight()
                    # cost = ttmodel.sum(slot_vars[group, sl] for sl in local_slots) * ponderation \
                    #        * self.local_weight()
                    ttmodel.add_to_group_cost(group, cost, week)

    def one_line_description(self):
        text = f"Il faut une pause déjeuner d'au moins {self.lunch_length} minutes " \
               f"entre {french_format(self.start_time)} et {french_format(self.end_time)}"
        try:
            text += " les " + ', '.join([wd for wd in self.weekdays])
        except ObjectDoesNotExist:
            pass
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        else:
            text += " pour tous les groupes"

        if self.train_progs.exists():
            text += ' de ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        else:
            text += " de toutes les promos."
        return text