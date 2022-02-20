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
from TTapp.TTConstraints.TTConstraint import TTConstraint


class LimitedRoomChoices(TTConstraint):
    """
    Limit the possible rooms for the courses
    Attributes are cumulative :
        limit the room choice for the courses of this/every tutor, of this/every module, for this/every group ...
    """
    module = models.ForeignKey('base.Module',
                               null=True,
                               default=None,
                               blank=True,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.StructuralGroup',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    course_type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              blank=True,
                              on_delete=models.CASCADE)
    possible_rooms = models.ManyToManyField('base.Room',
                                            related_name="limited_rooms")

    def enrich_model(self, ttmodel, week, ponderation=1.):
        fc = self.get_courses_queryset_by_attributes(ttmodel, week)
        possible_rooms = self.possible_rooms.values_list()
        if self.tutor is None:
            relevant_var_dic = ttmodel.TTrooms
        else:
            relevant_var_dic = {(sl, c, rg): ttmodel.add_conjunct(ttmodel.TTrooms[(sl, c, rg)],
                                                                  ttmodel.TTinstructors[sl, c, self.tutor])
                            for c in fc
                            for sl in ttmodel.wdb.compatible_slots[c]
                            for rg in ttmodel.wdb.course_rg_compat[c] if rg not in possible_rooms }
        relevant_sum = ttmodel.sum(relevant_var_dic[(sl, c, rg)]
                                   for c in fc
                                   for sl in ttmodel.wdb.compatible_slots[c]
                                   for rg in ttmodel.wdb.course_rg_compat[c] if rg not in possible_rooms)
        if self.weight is not None:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * relevant_sum, week=week)
        else:
            ttmodel.add_constraint(relevant_sum, '==', 0,
                                   Constraint(constraint_type=ConstraintType.LIMITED_ROOM_CHOICES,
                                              instructors=self.tutor, groups=self.group, modules=self.module,
                                              rooms=possible_rooms))

    def one_line_description(self):
        text = "Les "
        if self.course_type:
            text += str(self.course_type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_progs.exists():
            text += ' en ' + str(self.train_progs.all())
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'en salle "
        for sl in self.possible_rooms.values_list():
            text += str(sl) + ', '
        return text








