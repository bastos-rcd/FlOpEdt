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
from TTapp.slots import slots_filter
from TTapp.TTConstraints.TTConstraint import TTConstraint
from TTapp.TTConstraints.groups_constraints import considered_basic_groups
from TTapp.TTConstraints.tutors_constraints import considered_tutors
from django.utils.translation import gettext_lazy as _


class StabilizeTutorsCourses(TTConstraint):
    """
    Allow to really stabilize the courses of some/all tutor
    --> In this case, each course c scheduled:
        - in a unused slot costs 1,
        - in a unused day for tutor group cost ponderation
    """
    tutors = models.ManyToManyField('people.Tutor',blank=True)
    work_copy = models.PositiveSmallIntegerField(default=0)
    fixed_days = ArrayField(models.CharField(max_length=2,
                                             choices=Day.CHOICES), blank=True, null=True)

    class Meta:
        verbose_name = _('Stabilize tutors courses')
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['tutors'])
        return attributes

    def enrich_ttmodel(self, ttmodel, week, ponderation=5):
        tutors_to_be_considered = considered_tutors(self, ttmodel)
        ttmodel.wdb.sched_courses = ttmodel.wdb.sched_courses.filter(work_copy=self.work_copy)
        sched_courses = ttmodel.wdb.sched_courses.filter(course__week=week)

        for sl in slots_filter(ttmodel.wdb.courses_slots, week=week):
            for i in tutors_to_be_considered:
                if not sched_courses.filter(start_time__lt=sl.end_time,
                                            start_time__gt=sl.start_time - F('course__type__duration'),
                                            day=sl.day.day,
                                            tutor=i):
                    relevant_sum = ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)]
                                               for c in ttmodel.wdb.possible_courses[i]
                                                & ttmodel.wdb.compatible_courses[sl])

                    if self.weight is None:
                        ttmodel.add_constraint(relevant_sum, '==', 0,
                                               Constraint(constraint_type=ConstraintType.STABILIZE_ENRICH_MODEL,
                                                          instructors=i))
                    else:
                        ttmodel.add_to_inst_cost(i, self.local_weight() * relevant_sum, week=week)
                        if not sched_courses.filter(tutor=i,
                                                    day=sl.day.day):
                            ttmodel.add_to_inst_cost(i, self.local_weight() * ponderation * relevant_sum, week=week)

        if self.fixed_days:
            pass
            # Attention, les fixed_days doivent être des couples jour-semaine!!!!
            # for day in days_filter(self.fixed_days.all(), week=week):
            #     for sc in sched_courses.filter(slot__jour=day):
            #         ttmodel.add_constraint(ttmodel.TT[(sc.slot, sc.course)], '==', 1)
            #     for sc in sched_courses.exclude(slot__day=day):
            #         for sl in ttmodel.wdb.slots.filter(day=day):
            #             ttmodel.add_constraint(ttmodel.TT[(sl, sc.course)], '==', 0)

    def one_line_description(self):
        text = "Minimiser les changements"
        if self.tutors.exists():
            text += ' de ' + ', '.join([t.username for t in self.tutors.all()])
        if self.train_progs.count():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        text += ': copie ' + str(self.work_copy)
        return text


class StabilizeGroupsCourses(TTConstraint):
    """
    Allow to really stabilize the courses of some/all tutor
    --> In this case, each course c scheduled:
        - in a unused slot costs 1,
        - in a unused day for tutor group cost ponderation
    """
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)
    work_copy = models.PositiveSmallIntegerField(default=0)
    fixed_days = ArrayField(models.CharField(max_length=2,
                                             choices=Day.CHOICES), blank=True, null=True)

    class Meta:
        verbose_name = _('Stabilize groups courses')
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['groups'])
        return attributes

    def enrich_ttmodel(self, ttmodel, week, ponderation=5):
        basic_groups_to_be_considered = considered_basic_groups(self, ttmodel)
        ttmodel.wdb.sched_courses = ttmodel.wdb.sched_courses.filter(work_copy=self.work_copy)
        sched_courses = ttmodel.wdb.sched_courses.filter(course__week=week)

        for bg in basic_groups_to_be_considered:
            for sl in slots_filter(ttmodel.wdb.courses_slots, week=week):
                if not sched_courses.filter(course__groups__in=bg.and_ancestors(),
                                            day=sl.day):
                    considered_courses = ttmodel.wdb.courses_for_basic_group[bg] & ttmodel.wdb.compatible_courses[sl]
                    relevant_sum = ttmodel.sum(ttmodel.TT[(sl, c)] for c in considered_courses)
                    if self.weight is None:
                        ttmodel.add_constraint(relevant_sum, '==', 0,
                                               Constraint(constraint_type=ConstraintType.STABILIZE_ENRICH_MODEL,
                                                          groups=bg))
                    else:
                        ttmodel.add_to_group_cost(bg, self.local_weight() * ponderation * relevant_sum, week=week)

        if self.fixed_days:
            pass
            # Attention, les fixed_days doivent être des couples jour-semaine!!!!
            # for day in days_filter(self.fixed_days.all(), week=week):
            #     for sc in sched_courses.filter(slot__jour=day):
            #         ttmodel.add_constraint(ttmodel.TT[(sc.slot, sc.course)], '==', 1)
            #     for sc in sched_courses.exclude(slot__day=day):
            #         for sl in ttmodel.wdb.slots.filter(day=day):
            #             ttmodel.add_constraint(ttmodel.TT[(sl, sc.course)], '==', 0)

    def one_line_description(self):
        text = "Minimiser les changements"
        if self.groups.exists():
            text += ' des groupes ' + ', '.join([g.full_name for g in self.groups.all()])
        if self.train_progs.count():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        text += ': copie ' + str(self.work_copy)
        return text


class StabilizationThroughWeeks(TTConstraint):
    courses = models.ManyToManyField('base.Course')

    class Meta:
        verbose_name = _('Stabilization through weeks')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, week, ponderation=1):
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
