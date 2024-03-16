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

# from django.contrib.auth.models import User

# from caching.base import CachingManager, CachingMixin

from TTapp.ilp_constraints.constraint_type import ConstraintType

from TTapp.models import TimetableConstraint


class ReasonableDays(TimetableConstraint):
    """
    Allow to limit long days (with the first and last slot of a day). For a
    given parameter,
    a None value builds the constraint for all possible values,
    e.g. promo = None => the constraint holds for all promos.
    """
    groups = models.ManyToManyField('base.models.StructuralGroup',
                                    blank=True,
                                    related_name="reasonable_day_constraints")
    tutors = models.ManyToManyField('people.Tutor',
                                    blank=True,
                                    related_name="reasonable_day_constraints")

    def get_courses_queryset(self, ttmodel, tutor=None, group=None, train_prog=None):
        """
        Filter courses depending on constraints parameters
        """
        courses_qs = ttmodel.wdb.courses
        courses_filter = {}

        if tutor is not None:
            courses_filter['tutor'] = tutor

        if group is not None:
            courses_filter['group'] = group

        if train_prog is not None:
            courses_filter['group__train_prog'] = train_prog

        return courses_qs.filter(**courses_filter)


    def update_combinations(self, ttmodel, slot_boundaries, combinations, tutor=None, group=None, train_prog=None):
        """
        Update courses combinations for slot boundaries with all courses
        corresponding to the given filters (tutors, groups)
        """
        courses_query = self.get_courses_queryset(ttmodel, tutor=tutor, group=group, train_prog=train_prog)
        courses_set = set(courses_query)

        for first_slot, last_slot in slot_boundaries:
            while courses_set:
                c1 = courses_set.pop()
                for c2 in courses_set:
                    combinations.add(((first_slot, c1), (last_slot, c2),))


    def register_expression(self, ttmodel, ponderation, combinations):
        """
        Update model with expressions corresponding to
        all courses combinations
        """
        for first, last in combinations:
            if self.weight is not None:
                conj_var = ttmodel.add_conjunct(ttmodel.TT[first], ttmodel.TT[last])
                ttmodel.obj += self.local_weight() * ponderation * conj_var
            else:
                ttmodel.add_constraint(ttmodel.TT[first] + ttmodel.TT[last], '<=', 1,
                                       constraint_type=ConstraintType.REGISTER_EXPRESSION)


    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
        # Using a set type ensure that all combinations are
        # unique throw tutor and group filters
        combinations = set()

        # Get two dicts with the first and last slot by day
        first_slots = set([slot for slot in ttmodel.wdb.courses_slots if slot.start_time <= 9 * 60])
        last_slots = set([slot for slot in ttmodel.wdb.courses_slots if slot.end_time > 18 * 60])
        slots = first_slots | last_slots


        slot_boundaries = {}
        for slot in slots:
            slot_boundaries.setdefault(slot.day, []).append(slot)

        # Create all combinations with slot boundaries for all courses
        # corresponding to the given filters (tutors, groups)
        try:
            if self.tutors.count():
                for tutor in self.tutors.all():
                    self.update_combinations(ttmodel, slot_boundaries.values(), combinations, tutor=tutor)
            elif self.groups.count():
                for group in self.groups.all():
                    self.update_combinations(ttmodel, slot_boundaries.values(), combinations, group=group)
            else:
                self.update_combinations(ttmodel, slot_boundaries.values(), combinations)
        except ValueError:
            self.update_combinations(ttmodel, slot_boundaries.values(), combinations)

        self.register_expression(ttmodel, ponderation, combinations)


    def one_line_description(self):
        text = "Des journées pas trop longues"
        if self.tutors.count():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        if self.train_progs.count():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.groups.count():
            text += ' avec les groupes ' + ', '.join([group for group in self.groups.all()])
        return text


    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['groups', 'tutors'])
        return attributes


class AvoidBothTimes(TimetableConstraint):
    """
    Avoid the use of two slots
    Idéalement, on pourrait paramétrer slot1, et slot2 à partir de slot1... Genre slot1
    c'est 8h n'importe quel jour, et slot2 14h le même jour...
    """
    time1 = models.PositiveSmallIntegerField()  # FIXME : time with TimeField or DurationField
    time2 = models.PositiveSmallIntegerField()  # FIXME : time with TimeField or DurationField
    group = models.ForeignKey('base.models.StructuralGroup', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['group', 'tutor'])
        return attributes

    def enrich_ttmodel(self, ttmodel, ponderation=1):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.train_prog is not None:
            fc = fc.filter(group__train_prog=self.train_prog)
        if self.group:
            fc = fc.filter(group=self.group)
        slots1 = set([slot for slot in ttmodel.wdb.courses_slots if slot.start_time <= self.time1 < slot.end_time])
        slots2 = set([slot for slot in ttmodel.wdb.courses_slots if slot.start_time <= self.time2 < slot.end_time])
        for c1 in fc:
            for c2 in fc.exclude(id__lte=c1.id):
                for sl1 in slots1:
                    for sl2 in slots2:
                        if self.weight is not None:
                            conj_var = ttmodel.add_conjunct(
                                ttmodel.TT[(sl1, c1)],
                                ttmodel.TT[(sl2, c2)])
                            ttmodel.obj += self.local_weight() * ponderation * conj_var
                        else:
                            ttmodel.add_constraint(ttmodel.TT[(sl1, c1)]
                                                   + ttmodel.TT[(sl2, c2)],
                                                   '<=',
                                                   1,
                                                   constraint_type=ConstraintType.AVOID_BOTH_TIME, courses=[c1, c2],
                                                   slots=[sl1, sl2])

    def one_line_description(self):
        text = "Pas à la fois à " + str(self.time1/60) + "h et à" + str(self.time2/60) + "h."
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        return text




class LimitedStartTimeChoices(TimetableConstraint):
    """
    Limit the possible slots for the courses
    """

    module = models.ForeignKey('base.Module',
                               null=True,
                               default=None,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.models.StructuralGroup',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    possible_start_times = ArrayField(models.PositiveSmallIntegerField())  # FIXME : time with TimeField or DurationField




    def enrich_ttmodel(self, ttmodel, ponderation=1.):
        fc = self.considered_courses(ttmodel)
        possible_slots_ids = set(slot.id for slot in ttmodel.wdb.courses_slots
                                 if slot.start_time in self.possible_start_times.values_list())

        for c in fc:
            for sl in ttmodel.wdb.courses_slots.exclude(id__in=possible_slots_ids):
                if self.weight is not None:
                    ttmodel.obj += self.local_weight() * ponderation * ttmodel.TT[(sl, c)]
                else:
                    ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0, constraint_type=ConstraintType.LIMITED_START_TIME_CHOICES,
                                           courses=fc, slots=sl)

    def one_line_description(self):
        text = "Les "
        if self.type:
            text += str(self.type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'à "
        for sl in self.possible_start_times.values_list():
            if sl % 60==0:
                text += str(sl//60) + 'h, '
            else:
                text += str(sl//60) + 'h' + str(sl % 60) + ', '
        return text


class LimitedRoomChoices(TimetableConstraint):
    """
    Limit the possible rooms for the cources
    """
    module = models.ForeignKey('base.Module',
                               null=True,
                               default=None,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.models.StructuralGroup',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    possible_rooms = models.ManyToManyField('base.Room',
                                            related_name="limited_rooms")

    def enrich_ttmodel(self, ttmodel, ponderation=1.):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.module is not None:
            fc = fc.filter(module=self.module)
        if self.type is not None:
            fc = fc.filter(type=self.type)
        if self.group is not None:
            fc = fc.filter(group=self.group)
        possible_rooms_ids = self.possible_rooms.values_list('id', flat=True)

        for c in fc:
            for sl in ttmodel.wdb.courses_slots:
                for rg in ttmodel.wdb.room_groups.filter(types__in=[c.room_type]).exclude(id__in = possible_rooms_ids):
                    if self.weight is not None:
                        ttmodel.obj += self.local_weight() * ponderation * ttmodel.TTrooms[(sl, c, rg)]
                    else:
                        ttmodel.add_constraint(ttmodel.TTrooms[(sl, c,rg)], '==', 0,
                                               constraint_type=ConstraintType.LIMITED_ROOM_CHOICES, courses=c, slots=sl, rooms=rg)

    def one_line_description(self):
        text = "Les "
        if self.type:
            text += str(self.type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'en salle "
        for sl in self.possible_rooms.values_list():
            text += str(sl) + ', '
        return text
