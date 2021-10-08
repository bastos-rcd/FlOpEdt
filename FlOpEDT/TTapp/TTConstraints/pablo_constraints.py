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

from TTapp.TTConstraint import TTConstraint
from TTapp.ilp_constraints.constraint import Constraint, ConstraintType
from django.core.validators import MinValueValidator, MaxValueValidator
from TTapp.TTConstraints.tutors_constraints import considered_tutors
from TTapp.slots import slots_filter, days_filter, Slot
from base.timing import french_format



class LimitUndesiredSlotsPerWeek(TTConstraint):
    """
    Allow to limit the number of undesired slots per week
    start_time and end_time are in minuts from 0:00 AM
    """

    tutors = models.ManyToManyField('people.Tutor', blank=True)
    slot_start_time = models.PositiveSmallIntegerField()
    slot_end_time = models.PositiveSmallIntegerField()
    max_number = models.PositiveSmallIntegerField(validators=[MaxValueValidator(7)])

    def enrich_model(self, ttmodel, week, ponderation=1):
        tutor_to_be_considered = considered_tutors(self, ttmodel)
        days = days_filter(ttmodel.wdb.days, week=week)
        undesired_slots = [Slot(day=day, start_time=self.slot_start_time, end_time=self.slot_end_time)
                             for day in days]
        for tutor in tutor_to_be_considered:
            considered_courses = self.get_courses_queryset_by_parameters(tutor=tutor)
            expr = ttmodel.lin_expr()
            for undesired_slot in undesired_slots:
                expr += ttmodel.add_floor(
                    ttmodel.sum(ttmodel.TTinstructors[(sl, c, tutor)]
                                for c in considered_courses
                                for sl in slots_filter(ttmodel.wdb.courses_slots,
                                                       simultaneous_to=undesired_slot)
                                & ttmodel.wdb.compatible_slots[c]),
                    1,
                    len(considered_courses))
            if self.weight is None:
                ttmodel.add_constraint(expr, '<=', self.max_number,
                                       Constraint(constraint_type=ConstraintType.Undesired_slots_limit,
                                                  tutors=tutor))
            else:
                for i in range(self.max_number+1, len(days)+1):
                    cost = self.local_weight() * ponderation
                    undesired_situation = ttmodel.add_floor(expr, i, len(days))
                    ttmodel.add_to_inst_cost(tutor, cost * undesired_situation, week)
                    cost *= 2

    def one_line_description(self):
        text = ""
        if self.tutors.exists():
            text += ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            text += "Les profs"
        text += f" n'ont pas cours plus de {self.max_number} jours par semaine " \
               f"entre {french_format(self.slot_start_time)} et {french_format(self.slot_end_time)}"
        return text