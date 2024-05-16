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

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from base.timing import Time
from base.models import SchedulingPeriod, ScheduledCourse, Module
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.slots import days_filter, slots_filter
from TTapp.TimetableConstraints.timetable_constraint import TimetableConstraint

if TYPE_CHECKING:
    from TTapp.timetable_model import TimetableModel


def build_fd_or_apm_period_slots(ttmodel, day, apm_period):
    if apm_period is None:
        return slots_filter(ttmodel.data.courses_slots, day=day)
    return slots_filter(ttmodel.data.courses_slots, day=day, apm=apm_period)


class LimitTimePerPeriod(TimetableConstraint):
    """
    Abstract class : Limit the number of hours (of a given course_type) in every day/half-day
    """

    course_type = models.ForeignKey(
        "base.CourseType", on_delete=models.CASCADE, null=True, blank=True
    )
    max_time = models.DurationField(verbose_name=_("max_time"))
    FULL_DAY = "fd"
    HALF_DAY = "hd"
    PERIOD_CHOICES = ((FULL_DAY, "Full day"), (HALF_DAY, "Half day"))
    fhd_period = models.CharField(
        max_length=2, choices=PERIOD_CHOICES, verbose_name=_("fhd_period")
    )

    class Meta:
        abstract = True

    @property
    def max_minutes(self):
        return self.max_time.total_seconds() / 60

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        raise NotImplementedError

    def one_line_description(self):
        raise NotImplementedError

    def is_satisfied_for_one_object(self, version, considered_courses):
        if not considered_courses:
            return True
        considered_scheduled_courses = ScheduledCourse.objects.filter(
            course__in=considered_courses, version=version
        )
        considered_dates = set(
            sc.date for sc in considered_scheduled_courses.distinct("date")
        )
        for date in considered_dates:
            date_considered_scheduled_courses = considered_scheduled_courses.filter(
                date=date
            )
            if self.fhd_period == self.FULL_DAY:
                total_minutes = sum(
                    sc.minutes for sc in date_considered_scheduled_courses
                )
                if total_minutes > self.max_minutes:
                    return False
                return True
            for apm in [Time.AM, Time.PM]:
                total_minutes = sum(
                    sc.minutes
                    for sc in date_considered_scheduled_courses
                    if sc.apm == apm
                )
                if total_minutes > self.max_minutes:
                    return False
                return True
            return False

    def is_satisfied_for(self, period, version):
        raise NotImplementedError

    def build_fd_or_apm_period_by_day(
        self, ttmodel: "TimetableModel", period: SchedulingPeriod
    ):
        if self.fhd_period == self.FULL_DAY:
            apm_periods = [None]
        else:
            apm_periods = ttmodel.possible_apms

        fd_or_apm_period_by_day = []
        for day in days_filter(ttmodel.data.days, period=period):
            for apm_period in apm_periods:
                fd_or_apm_period_by_day.append(
                    (
                        day,
                        apm_period,
                    )
                )

        return fd_or_apm_period_by_day

    def courses_to_consider(
        self, ttmodel, period: SchedulingPeriod, train_prog, tutor, module, group
    ):
        return set(
            self.get_courses_queryset_by_parameters(
                period,
                ttmodel,
                course_type=self.course_type,
                train_prog=train_prog,
                module=module,
                group=group,
                tutor=tutor,
            )
        )

    def build_apm_period_expression(
        self,
        ttmodel: "TimetableModel",
        day,
        apm_period,
        considered_courses,
        tutor=None,  # pylint: disable=unused-argument
    ):
        """
        Build the expression that represents the total number of minutes of considered_courses
        """
        expr = ttmodel.lin_expr()
        for slot in build_fd_or_apm_period_slots(ttmodel, day, apm_period):
            for course in considered_courses & ttmodel.data.compatible_courses[slot]:
                expr += ttmodel.scheduled[(slot, course)] * course.minutes

        return expr

    def enrich_model_for_one_object(
        self,
        ttmodel: "TimetableModel",
        period: SchedulingPeriod,
        ponderation,
        train_prog=None,
        tutor=None,
        module=None,
        group=None,
    ):
        considered_courses = self.courses_to_consider(
            ttmodel, period, train_prog, tutor, module, group
        )
        for day, fd_or_apm_period in self.build_fd_or_apm_period_by_day(
            ttmodel, period
        ):
            expr = self.build_apm_period_expression(
                ttmodel, day, fd_or_apm_period, considered_courses, tutor
            )

            if self.weight is not None:
                var = ttmodel.add_floor(expr, self.max_minutes + 1, 60 * 24)
                ttmodel.add_to_generic_cost(
                    self.local_weight() * ponderation * var, period=period
                )
            else:
                ttmodel.add_constraint(
                    expr,
                    "<=",
                    self.max_minutes,
                    Constraint(
                        constraint_type=ConstraintType.MAX_HOURS,
                        days=day,
                        modules=module,
                        instructors=tutor,
                        groups=group,
                    ),
                )


class LimitGroupsTimePerPeriod(LimitTimePerPeriod):  # , pond):
    """
    Bound the number of course time (of type 'type') per day/half day for some group

    Attributes:
        groups : the groups concerned by the limitation. All the groups of self.train_progs if None.
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    groups = models.ManyToManyField(
        "base.StructuralGroup", blank=True, related_name="Course_type_limits"
    )

    class Meta:
        verbose_name = _("Limit groups busy time per period")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1.0):
        for group in self.considered_basic_groups(ttmodel):
            self.enrich_model_for_one_object(ttmodel, period, ponderation, group=group)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["groups", "course_type", "train_progs"])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        if self.course_type is not None:
            type_value = self.course_type.name
        else:
            type_value = "Any"

        if self.groups.exists():
            groups_value = ", ".join([group.name for group in self.groups.all()])
        else:
            groups_value = "All"

        view_model["details"].update(
            {
                "course_type": type_value,
                "groups": groups_value,
            }
        )

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_time)
        if self.course_type is not None:
            text += " de " + str(self.course_type)
        text += " par "
        if self.fhd_period == self.FULL_DAY:
            text += "jour"
        else:
            text += "demie-journée"
        if self.groups.exists():
            text += " pour les groupes" + ", ".join(
                [group.name for group in self.groups.all()]
            )
        else:
            text += " pour tous les groupes"
        if self.train_progs.exists():
            text += " de " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " de toutes les promos."
        return text

    def is_satisfied_for(self, period, version):
        unsatisfied_groups = []
        for basic_group in self.considered_basic_groups():
            considered_courses = self.get_courses_queryset_by_parameters(
                period=period,
                group=basic_group,
                course_type=self.course_type,
                transversal_groups_included=True,
            )
            if not self.is_satisfied_for_one_object(version, considered_courses):
                unsatisfied_groups.append(basic_group)
        assert not unsatisfied_groups, (
            f"{self} is not satisfied for period {period} and version {version} :"
            f"{unsatisfied_groups}"
        )


class LimitModulesTimePerPeriod(LimitTimePerPeriod):
    """
    Bound the number of hours of courses (of type 'type') per day/half day
    Attributes:
        modules : the modules concerned by the limitation.
        All the modules of self.train_progs if None.
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    modules = models.ManyToManyField(
        "base.Module", blank=True, related_name="Course_type_limits"
    )
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)

    class Meta:
        verbose_name = _("Limit modules busy time per period")
        verbose_name_plural = verbose_name

    def considered_modules(self, ttmodel: "TimetableModel" = None):
        if ttmodel is None:
            modules_to_consider = Module.objects.filter(
                train_prog__department=self.department
            )
        else:
            modules_to_consider = ttmodel.data.modules

        if self.train_progs.exists():
            modules_to_consider = self.modules.filter(
                train_prog__in=self.considered_train_progs(ttmodel)
            )
        modules_to_consider = set(modules_to_consider)

        if self.modules.exists():
            modules_to_consider = modules_to_consider & set(self.modules.all())

        return modules_to_consider

    def enrich_ttmodel(self, ttmodel, period, ponderation=1.0):
        for module in self.considered_modules(ttmodel):
            for group in self.considered_basic_groups(ttmodel):
                self.enrich_model_for_one_object(
                    ttmodel, period, ponderation, module=module, group=group
                )

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["modules", "course_type", "train_progs"])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()

        if self.course_type is not None:
            type_value = self.course_type.name
        else:
            type_value = "Any"

        if self.modules.exists():
            module_value = ", ".join([module.abbrev for module in self.modules.all()])
        else:
            module_value = "All"

        view_model["details"].update(
            {
                "course_type": type_value,
                # 'tutor': tutor_value,
                "modules": module_value,
            }
        )

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_time)
        if self.course_type:
            text += " de " + str(self.course_type)
        text += " par "
        if self.fhd_period == self.FULL_DAY:
            text += "jour"
        else:
            text += "demie-journée"
        if self.modules.exists():
            text += " de " + ", ".join([module.abbrev for module in self.modules.all()])
        else:
            text += " de chaque module"
        if self.train_progs.exists():
            text += " en " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " dans toutes les promos."

        return text

    def is_satisfied_for(self, period, version):
        unsatisfied_groups_and_modules = []
        for basic_group in self.considered_basic_groups():
            for module in self.considered_modules():
                considered_courses = self.get_courses_queryset_by_parameters(
                    period=period,
                    module=module,
                    course_type=self.course_type,
                    group=basic_group,
                    transversal_groups_included=True,
                )
                if not self.is_satisfied_for_one_object(version, considered_courses):
                    unsatisfied_groups_and_modules.append((basic_group, module))
        assert not unsatisfied_groups_and_modules, (
            f"{self} is not satisfied for period {period} and version {version} :"
            f"{unsatisfied_groups_and_modules}"
        )


class LimitTutorsTimePerPeriod(LimitTimePerPeriod):
    """
    Bound the time of tutor courses of type 'course_type' per day/half day for tutors
    Attributes:
        tutors : the tutors concerned by the limitation. All if None.

    """

    tutors = models.ManyToManyField(
        "people.Tutor", blank=True, related_name="Course_type_limits"
    )

    class Meta:
        verbose_name = _("Limit tutors busy time per period")
        verbose_name_plural = verbose_name

    def build_apm_period_expression(  # pylint: disable=arguments-renamed
        self, ttmodel, day, fd_or_apm_period, considered_courses, tutor=None
    ):
        expr = ttmodel.lin_expr()
        for slot in build_fd_or_apm_period_slots(ttmodel, day, fd_or_apm_period):
            for course in considered_courses & ttmodel.data.compatible_courses[slot]:
                expr += ttmodel.assigned[(slot, course, tutor)] * course.minutes

        return expr

    def enrich_ttmodel(self, ttmodel, period, ponderation=1.0):
        for tutor in self.considered_tutors(ttmodel):
            self.enrich_model_for_one_object(ttmodel, period, ponderation, tutor=tutor)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["tutors", "course_type"])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()

        if self.course_type is not None:
            type_value = self.course_type.name
        else:
            type_value = "Any"

        if self.tutors.exists():
            tutor_value = ", ".join([tutor.username for tutor in self.tutors.all()])
        else:
            tutor_value = "All"

        view_model["details"].update(
            {
                "course_type": type_value,
                "tutors": tutor_value,
            }
        )

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_time)
        if self.course_type:
            text += " de " + str(self.course_type)
        text += " par "
        if self.fhd_period == self.FULL_DAY:
            text += "jour"
        else:
            text += "demie-journée"
        if self.tutors.exists():
            text += " pour " + ", ".join(
                [tutor.username for tutor in self.tutors.all()]
            )
        else:
            text += " pour tous les profs "
        if self.train_progs.exists():
            text += " en " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        return text

    def is_satisfied_for(self, period, version):
        unsatisfied_tutors = []
        for tutor in self.considered_tutors():
            considered_courses = self.get_courses_queryset_by_parameters(period=period)
            considered_scheduled_courses = ScheduledCourse.objects.filter(
                (Q(tutor=tutor) | Q(course__supp_tutors=tutor)),
                course__in=considered_courses,
                version=version,
            )
            considered_courses = set(sc.course for sc in considered_scheduled_courses)
        assert not unsatisfied_tutors, (
            f"{self} is not satisfied for period {period} and version {version} :"
            f"{unsatisfied_tutors}"
        )


class LimitCourseTypeTimePerPeriod(LimitTimePerPeriod):  # , pond):
    """
    Bound the number of course time (of type 'type') per day/half day
    """

    class Meta:
        verbose_name = _("Limit course type time, regardless of tutor, module or group")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1.0):
        self.enrich_model_for_one_object(ttmodel, period, ponderation)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["course_type"])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        if self.course_type is not None:
            type_value = self.course_type.name
        else:
            type_value = "Any"

        view_model["details"].update({"course_type": type_value})

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.max_time)
        if self.course_type is not None:
            text += "de " + str(self.course_type)
        text += " par "
        if self.fhd_period == self.FULL_DAY:
            text += "jour"
        else:
            text += "demie-journée"
        if self.train_progs.exists():
            text += " pour " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " pour toutes les promos."
        return text

    def is_satisfied_for(self, period, version):
        considered_courses = self.get_courses_queryset_by_parameters(
            period=period, course_type=self.course_type
        )
        assert self.is_satisfied_for_one_object(version, considered_courses), (
            f"{self} is not satisfied for period {period} and version {version} :"
            f"{self.course_type}"
        )