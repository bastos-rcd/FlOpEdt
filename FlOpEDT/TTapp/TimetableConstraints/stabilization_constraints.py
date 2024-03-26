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
from django.utils.translation import gettext_lazy as _

from base.timing import Day
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.slots import slots_filter
from TTapp.TimetableConstraints.TimetableConstraint import TimetableConstraint
from TTapp.TimetableConstraints.tutors_constraints import considered_tutors


class StabilizeTutorsCourses(TimetableConstraint):
    """
    Allow to really stabilize the courses of some/all tutor
    --> In this case, each course c scheduled:
        - in a unused slot costs 1,
        - in a unused day for tutor group cost ponderation
    """

    tutors = models.ManyToManyField("people.Tutor", blank=True)
    version = models.ForeignKey(
        "base.TimetableVersion", on_delete=models.CASCADE, null=True
    )
    fixed_days = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Stabilize tutors courses")
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["tutors"])
        return attributes

    def enrich_ttmodel(self, ttmodel, period, ponderation=5):
        tutors_to_be_considered = considered_tutors(self, ttmodel)
        ttmodel.data.sched_courses = ttmodel.data.sched_courses.filter(
            version=self.version
        )
        sched_courses = ttmodel.data.sched_courses.filter(course__period=period)

        for sl in slots_filter(ttmodel.data.courses_slots, period=period):
            for i in tutors_to_be_considered:
                if not sched_courses.filter(
                    start_time__lt=sl.end_time,
                    start_time__gt=sl.start_time - F("course__type__duration"),
                    day=sl.day.day,
                    tutor=i,
                ):
                    relevant_sum = ttmodel.sum(
                        ttmodel.assigned[(sl, c, i)]
                        for c in ttmodel.data.possible_courses[i]
                        & ttmodel.data.compatible_courses[sl]
                    )

                    if self.weight is None:
                        ttmodel.add_constraint(
                            relevant_sum,
                            "==",
                            0,
                            Constraint(
                                constraint_type=ConstraintType.STABILIZE_ENRICH_MODEL,
                                instructors=i,
                            ),
                        )
                    else:
                        ttmodel.add_to_inst_cost(
                            i, self.local_weight() * relevant_sum, period=period
                        )
                        if not sched_courses.filter(tutor=i, day=sl.day.day):
                            ttmodel.add_to_inst_cost(
                                i,
                                self.local_weight() * ponderation * relevant_sum,
                                period=period,
                            )

        if self.fixed_days:
            pass
            # Attention, les fixed_days doivent être des couples jour-semaine!!!!
            # for day in days_filter(self.fixed_days.all(), period=period):
            #     for sc in sched_courses.filter(slot__jour=day):
            #         ttmodel.add_constraint(ttmodel.scheduled[(sc.slot, sc.course)], '==', 1)
            #     for sc in sched_courses.exclude(slot__day=day):
            #         for sl in ttmodel.data.slots.filter(day=day):
            #             ttmodel.add_constraint(ttmodel.scheduled[(sl, sc.course)], '==', 0)

    def one_line_description(self):
        text = "Minimiser les changements"
        if self.tutors.exists():
            text += " de " + ", ".join([t.username for t in self.tutors.all()])
        text += ": copie " + str(self.version)
        return text


class StabilizeGroupsCourses(TimetableConstraint):
    """
    Allow to really stabilize the courses of some/all tutor
    --> In this case, each course c scheduled:
        - in a unused slot costs 1,
        - in a unused day for tutor group cost ponderation
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)
    version = models.ForeignKey(
        "base.TimetableVersion", on_delete=models.CASCADE, null=True
    )
    fixed_days = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Stabilize groups courses")
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["groups", "train_progs"])
        return attributes

    def enrich_ttmodel(self, ttmodel, period, ponderation=5):
        basic_groups_to_be_considered = self.considered_basic_groups(ttmodel)
        ttmodel.data.sched_courses = ttmodel.data.sched_courses.filter(
            version=self.version
        )
        sched_courses = ttmodel.data.sched_courses.filter(course__period=period)

        for bg in basic_groups_to_be_considered:
            for sl in slots_filter(ttmodel.data.courses_slots, period=period):
                if not sched_courses.filter(
                    course__groups__in=bg.and_ancestors(), day=sl.day
                ):
                    considered_courses = (
                        ttmodel.data.courses_for_basic_group[bg]
                        & ttmodel.data.compatible_courses[sl]
                    )
                    relevant_sum = ttmodel.sum(
                        ttmodel.scheduled[(sl, c)] for c in considered_courses
                    )
                    if self.weight is None:
                        ttmodel.add_constraint(
                            relevant_sum,
                            "==",
                            0,
                            Constraint(
                                constraint_type=ConstraintType.STABILIZE_ENRICH_MODEL,
                                groups=bg,
                            ),
                        )
                    else:
                        ttmodel.add_to_group_cost(
                            bg,
                            self.local_weight() * ponderation * relevant_sum,
                            period=period,
                        )

        if self.fixed_days:
            pass
            # Attention, les fixed_days doivent être des couples jour-semaine!!!!
            # for day in days_filter(self.fixed_days.all(), period=period):
            #     for sc in sched_courses.filter(slot__jour=day):
            #         ttmodel.add_constraint(ttmodel.scheduled[(sc.slot, sc.course)], '==', 1)
            #     for sc in sched_courses.exclude(slot__day=day):
            #         for sl in ttmodel.data.slots.filter(day=day):
            #             ttmodel.add_constraint(ttmodel.scheduled[(sl, sc.course)], '==', 0)

    def one_line_description(self):
        text = "Minimiser les changements"
        if self.groups.exists():
            text += " des groupes " + ", ".join(
                [g.full_name for g in self.groups.all()]
            )
        if self.train_progs.count():
            text += " en " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        text += ": version " + str(self.version)
        return text


class StabilizationThroughPeriods(TimetableConstraint):
    courses = models.ManyToManyField("base.Course")

    class Meta:
        verbose_name = _("Stabilization through periods")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        if period != ttmodel.periods[0]:
            return
        ttmodel_courses_id = [c.id for c in ttmodel.data.courses]
        courses = self.courses.filter(id__in=ttmodel_courses_id)
        periods = [c.period for c in courses.distinct("period")]
        courses_data = [
            {"period": p, "courses": courses.filter(period=p)} for p in periods
        ]
        courses_data = [c for c in courses_data if len(c["courses"]) != 0]
        courses_data.sort(key=lambda c: len(c["courses"]))
        for i in range(len(courses_data) - 1):
            for sl0 in ttmodel.data.compatible_slots[courses_data[i]["courses"][0]]:
                sl1 = ttmodel.find_same_course_slot_in_other_period(
                    sl0, period, other_period=courses_data[i + 1]["period"]
                )
                ttmodel.add_constraint(
                    2
                    * ttmodel.sum(
                        ttmodel.scheduled[sl0, c0] for c0 in courses_data[i]["courses"]
                    )
                    - ttmodel.sum(
                        ttmodel.scheduled[sl1, c1]
                        for c1 in courses_data[i + 1]["courses"]
                    ),
                    "<=",
                    1,
                    Constraint(
                        constraint_type=ConstraintType.STABILIZE_THROUGH_PERIODS
                    ),
                )

    def one_line_description(self):
        return "Stabilization through periods"
