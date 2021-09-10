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

from django.db.models import F

from base.timing import Day

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.slots import Slot, slots_filter
from TTapp.TTConstraint import TTConstraint


class Stabilize(TTConstraint):
    """
    Allow to realy stabilize the courses of a category
    If general is true, none of the other (except week and work_copy) is
    relevant.
    --> In this case, each course c placed:
        - in a unused slot costs 1,
        - in a unused half day (for tutor and/or group) cost ponderation
    If general is False, it Fixes train_prog/tutor/group courses (or tries to if
    self.weight)
    """
    general = models.BooleanField(
        verbose_name='Stabiliser tout?',
        default=False)

    group = models.ForeignKey('base.StructuralGroup', null=True, default=None, on_delete=models.CASCADE)
    module = models.ForeignKey('base.Module', null=True, default=None, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    course_type = models.ForeignKey('base.CourseType', null=True, default=None, on_delete=models.CASCADE)
    work_copy = models.PositiveSmallIntegerField(default=0)
    fixed_days = ArrayField(models.CharField(max_length=2,
                                             choices=Day.CHOICES), blank=True, null=True)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['group', 'module', 'tutor', 'course_type'])
        return attributes

    def enrich_model(self, ttmodel, week, ponderation=1):
        sched_courses = ttmodel.wdb.sched_courses.filter(work_copy=self.work_copy, course__week=week)
        if self.fixed_days:
            pass
            # Attention, les fixed_days doivent être des couples jour-semaine!!!!
            # for day in days_filter(self.fixed_days.all(), week=week):
            #     for sc in sched_courses.filter(slot__jour=day):
            #         ttmodel.add_constraint(ttmodel.TT[(sc.slot, sc.course)], '==', 1)
            #     for sc in sched_courses.exclude(slot__day=day):
            #         for sl in ttmodel.wdb.slots.filter(day=day):
            #             ttmodel.add_constraint(ttmodel.TT[(sl, sc.course)], '==', 0)

        if self.general:
            # nb_changements_I=dict(zip(ttmodel.wdb.instructors,[0 for i in ttmodel.wdb.instructors]))
            for sl in slots_filter(ttmodel.wdb.courses_slots, week=week):
                for c in ttmodel.wdb.compatible_courses[sl]:
                    for g in c.groups.all():
                        if not sched_courses.filter(course__groups=g,
                                                    day=sl.day):
                            ttmodel.add_to_generic_cost(ponderation * ttmodel.TT[(sl, c)], week=week)
                for i in ttmodel.wdb.instructors:
                    for c in ttmodel.wdb.possible_courses[i] & ttmodel.wdb.compatible_courses[sl]:
                        if not sched_courses.filter(start_time__lt=sl.end_time,
                                                    start_time__gt=sl.start_time - F('course__type__duration'),
                                                    day=sl.day,
                                                    tutor=i):
                            ttmodel.add_to_generic_cost(ponderation * ttmodel.TTinstructors[(sl, c, i)], week=week)
                            # nb_changements_I[c.tutor]+=ttmodel.TT[(sl,c)]
                        if not sched_courses.filter(tutor=i,
                                                    day=sl.day):
                            ttmodel.add_to_generic_cost(ponderation * ttmodel.TTinstructors[(sl, c, i)], week=week)
                            # nb_changements_I[i]+=ttmodel.TT[(sl,c)]

        else:
            # TO BE CHECKED !!!
            pass
            # fc = self.get_courses_queryset_by_attributes(ttmodel, week)
            # for c in fc:
            #     sched_c = ttmodel.wdb \
            #         .sched_courses \
            #         .get(course=c,
            #              work_copy=self.work_copy)
            #     chosen_slot = Slot(start_time=sched_c.start_time,
            #                        end_time=sched_c.end_time,
            #                        day=sched_c.day)
            #     if self.weight is not None:
            #         ttmodel.add_to_generic_cost(-self.local_weight() \
            #                        * ponderation * ttmodel.TT[(chosen_slot, c)], week=week)
            #
            #     else:
            #         for slot in ttmodel.wdb.compatible_slots[c]:
            #             if not slot.is_simultaneous_to(chosen_slot):
            #                 ttmodel.add_constraint(ttmodel.TT[(slot, c)],
            #                                        '==',
            #                                        0,
            #                                        Constraint(constraint_type=ConstraintType.STABILIZE_ENRICH_MODEL,
            #                                                   courses=fc, slots=slot))


    def one_line_description(self):
        text = "Minimiser les changements"
        if self.course_type:
            text += " pour les " + str(self.course_type
                                       )
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.train_progs.count():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        if self.group:
            text += ' du groupe ' + str(self.group)
        text += ': copie ' + str(self.work_copy)
        return text


class StabilizationThroughWeeks(TTConstraint):
    courses = models.ManyToManyField('base.Course')

    def enrich_model(self, ttmodel, week, ponderation=1):
        if week != ttmodel.weeks[0]:
            return
        ttmodel_courses_id = [c.id for c in ttmodel.wdb.courses]
        courses = self.courses.filter(id__in=ttmodel_courses_id)
        weeks = [c.week for c in courses.distinct('week')]
        courses_data = [{'week': w, 'courses': courses.filter(week=w)} for w in weeks]
        courses_data = [c for c in courses_data if len(c['courses']) != 0]
        courses_data.sort(key=lambda c: len(c['courses']))
        for i in range(len(courses_data)-1):
            for sl0 in ttmodel.wdb.compatible_slots[courses_data[i]['courses'][0]]:
                sl1 = ttmodel.find_same_course_slot_in_other_week(sl0, courses_data[i+1]['week'])
                ttmodel.add_constraint(
                    2 * ttmodel.sum(ttmodel.TT[sl0, c0] for c0 in courses_data[i]['courses'])
                    - ttmodel.sum(ttmodel.TT[sl1, c1] for c1 in courses_data[i+1]['courses']),
                    '<=',
                    1, Constraint(constraint_type=ConstraintType.STABILIZE_THROUGH_WEEKS))

    def one_line_description(self):
        return "Stabilization through weeks"
