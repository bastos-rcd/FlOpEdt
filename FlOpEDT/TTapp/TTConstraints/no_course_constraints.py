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
from base.timing import Day
from people.models import Tutor


from TTapp.slots import slots_filter
from TTapp.TTConstraint import TTConstraint

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from .groups_constraints import considered_basic_groups


class NoCourseOnDay(TTConstraint):
    FULL_DAY = 'fd'
    AM = 'AM'
    PM = 'PM'
    PERIOD_CHOICES = ((FULL_DAY, 'Full day'), (AM, 'AM'), (PM, 'PM'))
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)
    weekday = models.CharField(max_length=2, choices=Day.CHOICES)

    class Meta:
        abstract = True

    def considered_slots(self, ttmodel, week):
        if self.period == self.FULL_DAY:
            considered_slots = slots_filter(ttmodel.wdb.courses_slots,
                                            week_day=self.weekday, week=week)
        else:
            considered_slots = slots_filter(ttmodel.wdb.courses_slots,
                                            week_day=self.weekday, apm=self.period, week=week)
        return considered_slots

    def considered_sum(self, ttmodel, week):
        raise NotImplementedError

    def enrich_model(self, ttmodel, week, ponderation=1):
        if self.weight is None:
            ttmodel.add_constraint(self.considered_sum(ttmodel, week),
                                   '==', 0,
                                   Constraint(constraint_type=ConstraintType.NO_COURSE_ON_DAY, weeks=week))
        else:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * self.considered_sum(ttmodel, week), week)


class NoGroupCourseOnDay(NoCourseOnDay):
    groups = models.ManyToManyField('base.Group', blank=True)
    course_types = models.ManyToManyField('base.CourseType', blank=True, related_name='no_course_on_days')

    def considered_courses(self, ttmodel):
        c_c = set(c for g in considered_basic_groups(self, ttmodel)
                  for c in ttmodel.wdb.courses_for_basic_group[g])
        if self.course_types.exists():
            c_c = set(c for c in c_c
                      if c.type in self.course_types.all())
        return c_c

    def considered_sum(self, ttmodel, week):
        return ttmodel.sum(ttmodel.TT[(sl, c)]
                           for c in self.considered_courses(ttmodel)
                           for sl in self.considered_slots(ttmodel, week) & ttmodel.wdb.compatible_slots[c])

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


class NoTutorCourseOnDay(NoCourseOnDay):
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    tutor_status = models.CharField(max_length=2, choices=Tutor.TUTOR_CHOICES, null=True, blank=True)

    def considered_tutors(self, ttmodel):
        if self.tutors.exists():
            tutors = set(t for t in ttmodel.wdb.instructors if t in self.tutors.all())
        else:
            tutors = set(ttmodel.wdb.instructors)
        if self.tutor_status is not None:
            tutors = set(t for t in tutors if t.status == self.tutor_status)
        return tutors

    def considered_sum(self, ttmodel, week):
        return ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)]
                           for i in self.considered_tutors(ttmodel)
                           for c in ttmodel.wdb.possible_courses[i]
                           for sl in self.considered_slots(ttmodel, week) & ttmodel.wdb.compatible_slots[c])

    def one_line_description(self):
        text = f"Aucun cours le {self.weekday}"
        if self.period != self.FULL_DAY:
            text += f" ({self.period})"
        if self.tutors.exists():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        if self.tutor_status is not None:
            text += f" (ne concerne que les {self.tutor_status} "
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        return text
