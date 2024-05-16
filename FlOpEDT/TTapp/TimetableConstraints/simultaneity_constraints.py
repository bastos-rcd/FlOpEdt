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
from django.utils.translation import gettext_lazy as _

from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.slots import slots_filter
from TTapp.TimetableConstraints.timetable_constraint import TimetableConstraint


class NotAloneForTheseCouseTypes(TimetableConstraint):
    """
    TimetableConstraint : Guarantees that any considered tutor
    will not be alone to do a course of this type/module
    (and will be in parallel to one of the guide tutors)
    """

    tutors = models.ManyToManyField(
        "people.Tutor",
        blank=True,
        verbose_name=_("tutors"),
        related_name="not_alone_as_tutor",
    )
    guide_tutors = models.ManyToManyField(
        "people.Tutor",
        blank=True,
        verbose_name=_("guide tutors"),
        related_name="not_alone_as_guide",
    )
    course_types = models.ManyToManyField("base.CourseType", blank=True)
    modules = models.ManyToManyField("base.Module", blank=True)

    class Meta:
        verbose_name = _("Not alone for these course types")
        verbose_name_plural = verbose_name

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model["details"]

        if self.tutors.exists():
            details.update(
                {"tutors": ", ".join([tutor.username for tutor in self.tutors.all()])}
            )

        if self.course_types.exists():
            details.update(
                {
                    "course_types": ", ".join(
                        [course_type.name for course_type in self.course_types.all()]
                    )
                }
            )

        if self.modules.exists():
            details.update(
                {"modules": ", ".join([module.name for module in self.modules.all()])}
            )

        return view_model

    def one_line_description(self):
        text = "Les profs "

        if self.tutors.exists():
            text += ", ".join([tutor.username for tutor in self.tutors.all()])

        text += "ont un prof en parallèle "

        if self.course_types.exists():
            text += " pour les types " + ", ".join(
                [course_type.name for course_type in self.course_types.all()]
            )
        else:
            text += "pour chaque type de cours"

        if self.modules.exists():
            text += " dans les modules " + ", ".join(
                [course_type.name for course_type in self.course_types.all()]
            )
        else:
            text += "dans tous les modules"

        return text

    def enrich_ttmodel(self, ttmodel, period, ponderation=10):
        considered_course_types = ttmodel.data.course_types
        if self.course_types.exists():
            considered_course_types &= set(self.course_types.all())
        considered_modules = set(ttmodel.data.modules)
        if self.modules.exists():
            considered_modules &= set(self.modules.all())
        tutors_to_consider = self.considered_tutors(ttmodel)
        guides_to_consider = set(ttmodel.data.instructors)
        if self.guide_tutors.exists():
            guides_to_consider &= set(self.guide_tutors.all())

        for tutor in tutors_to_consider:
            possible_tutor_guides = guides_to_consider - {tutor}
            for ct in considered_course_types:
                for m in considered_modules:
                    courses = set(
                        ttmodel.data.courses.filter(module=m, type=ct, period=period)
                    )
                    tutor_courses = courses & ttmodel.data.possible_courses[tutor]
                    if not ttmodel.data.possible_courses[tutor] & courses:
                        continue
                    for sl in slots_filter(ttmodel.data.courses_slots, period=period):
                        tutor_sum = ttmodel.sum(
                            ttmodel.assigned[sl, c, tutor]
                            for c in tutor_courses & ttmodel.data.compatible_courses[sl]
                        )
                        guide_tutors_sum = ttmodel.sum(
                            ttmodel.assigned[sl, c, g]
                            for g in possible_tutor_guides
                            for c in courses
                            & ttmodel.data.compatible_courses[sl]
                            & ttmodel.data.possible_courses[g]
                        )
                        if self.weight is None:
                            ttmodel.add_constraint(
                                tutor_sum - guide_tutors_sum,
                                "<=",
                                0,
                                Constraint(
                                    constraint_type=ConstraintType.NOT_ALONE,
                                    instructors=tutor,
                                    periods=period,
                                ),
                            )
                        else:
                            tutor_without_a_guide = ttmodel.add_var()
                            # if new_var is 1, then not_ok
                            ttmodel.add_constraint(
                                100 * tutor_without_a_guide
                                + (guide_tutors_sum - tutor_sum),
                                "<=",
                                99,
                            )

                            # if not_ok (t_s > g_t_s) then new_var is 1
                            ttmodel.add_constraint(
                                (tutor_sum - guide_tutors_sum)
                                - 100 * tutor_without_a_guide,
                                "<=",
                                0,
                            )
                            ttmodel.add_to_inst_cost(
                                tutor,
                                self.local_weight()
                                * ponderation
                                * tutor_without_a_guide,
                            )

    def is_satisfied_for(self, period, version):
        raise NotImplementedError


class ParallelizeCourses(TimetableConstraint):
    """
    TimetableConstraint : Guarantees that the total course time of certain class of courses
    do not exceed a certain bound
    """

    course_type = models.ForeignKey(
        "base.CourseType",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("course type"),
    )
    module = models.ForeignKey(
        "base.Module",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("module"),
    )
    desired_busy_slots_duration = models.DurationField(
        verbose_name=_("Desired busy slots duration")
    )

    class Meta:
        verbose_name = _("Parallelize courses")
        verbose_name_plural = verbose_name

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model["details"]

        if self.course_type is not None:
            details.update({"course_type": self.course_type.name})

        if self.module is not None:
            details.update({"modules": self.module.name})

        return view_model

    def one_line_description(self):
        text = (
            "Tous les cours sont concentrés en " f"{self.desired_busy_slots_duration}"
        )

        if self.course_type is not None:
            text += " pour le type " + self.course_type.name

        if self.module is not None:
            text += " pour le module " + self.course_type.name

        return text

    @property
    def desired_busy_slots_minutes(self):
        return self.desired_busy_slots_duration.total_seconds() / 60

    def enrich_ttmodel(self, ttmodel, period, ponderation=10):
        considered_courses = self.considered_courses(ttmodel)

        total_courses_duration = ttmodel.lin_expr()
        for sl in ttmodel.data.availability_slots:
            used_slot = ttmodel.add_floor(
                ttmodel.sum(
                    ttmodel.scheduled[course_slot, course]
                    for course_slot in slots_filter(
                        ttmodel.data.courses_slots, simultaneous_to=sl
                    )
                    for course in considered_courses
                    & ttmodel.data.compatible_courses[course_slot]
                ),
                1,
                1000,
            )
            total_courses_duration += sl.duration * used_slot
        if self.weight is None:
            ttmodel.add_constraint(
                total_courses_duration,
                "<=",
                self.desired_busy_slots_duration,
                Constraint(constraint_type=ConstraintType.LIMIT_BUSY_SLOTS),
            )
        else:
            cost = ttmodel.lin_expr()
            start = self.desired_busy_slots_duration
            end = sum(c.duration for c in considered_courses)
            step = (end - start) // 4
            for bound in range(start, end + 1, step):
                cost *= 2
                cost += ttmodel.add_floor(total_courses_duration, bound - 1, 100000)
            ttmodel.add_to_generic_cost(
                cost * self.local_weight() * ponderation, period
            )

    def is_satisfied_for(self, period, version):
        raise NotImplementedError