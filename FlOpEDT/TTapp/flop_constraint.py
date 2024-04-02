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

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from TTapp.slots import days_filter

from base.models import (
    Course,
    ScheduledCourse,
    SchedulingPeriod,
    TimeGeneralSettings,
    TimetableVersion,
    TrainingProgramme,
)

MAX_WEIGHT = 8


def all_subclasses(cls):
    return set(c for c in cls.__subclasses__() if not c._meta.abstract).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


class FlopConstraint(models.Model):
    """
    Abstract parent class of specific constraints that users may define

    Attributes:
        department : the department concerned by the constraint. Has to be filled.
        periods : the scheduling periods for which the constraint should be applied. All if None.
        weight : from 1 to max_weight if the constraint is optional, depending on its importance
                 None if the constraint is necessary
        is_active : usefull to de-activate a Constraint just before the generation
    """

    department = models.ForeignKey(
        "base.Department", null=True, on_delete=models.CASCADE
    )
    periods = models.ManyToManyField("base.SchedulingPeriod", blank=True)
    weight = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(MAX_WEIGHT)],
        null=True,
        default=None,
        blank=True,
    )
    title = models.CharField(max_length=30, null=True, default=None, blank=True)
    comment = models.CharField(max_length=100, null=True, default=None, blank=True)
    is_active = models.BooleanField(verbose_name=_("Is active?"), default=True)
    modified_at = models.DateField(auto_now=True)

    def is_satisfied_for(self, period: SchedulingPeriod, version: TimetableVersion):
        """
        Test if the constraint is satisfied for the given period and work copy
        """
        raise NotImplementedError

    def considered_dates(self, period, ttmodel=None):
        if ttmodel is None:
            dates_to_consider = days_filter(
                period.dates(), weekday=self.time_settings().weekdays
            )
        else:
            dates_to_consider = days_filter(ttmodel.data.dates, period=period)
        if hasattr(self, "dates"):
            dates_to_consider &= set(self.dates)
        if hasattr(self, "date"):
            dates_to_consider &= {self.date}
        if hasattr(self, "weekday"):
            dates_to_consider = days_filter(dates_to_consider, weekday=self.weekday)
        if hasattr(self, "weekdays"):
            dates_to_consider = days_filter(dates_to_consider, weekday_in=self.weekdays)
        return dates_to_consider

    def period_version_scheduled_courses_queryset(
        self, period: SchedulingPeriod, version: TimetableVersion
    ) -> models.QuerySet:
        """
        Return all scheduled courses of the given work copy for the given period
        """
        return ScheduledCourse.objects.filter(
            course__in=self.considered_courses(period), version=version
        ).select_related("course", "tutor", "room")

    def local_weight(self):
        if self.weight is None:
            return 10
        return float(self.weight) / MAX_WEIGHT

    class Meta:
        abstract = True

    def description(self):
        # Return a human readable constraint name
        return self.__doc__ or str(self)

    def get_viewmodel(self):
        """

        :return: a dictionnary with view-related data
        """

        if self.periods.exists():
            period_value = ",".join([f"{p.name} " for p in self.periods.all()])
        else:
            period_value = "All"

        return {
            "model": self.__class__.__name__,
            "pk": self.pk,
            "is_active": self.is_active,
            "name": self._meta.verbose_name,
            "description": self.description(),
            "explanation": self.one_line_description(),
            "comment": self.comment,
            "details": {
                "periods": period_value,
                "weight": self.weight,
            },
        }

    def one_line_description(self):
        # Return a human readable constraint name with its attributes
        raise NotImplementedError

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        return [
            "department",
        ]

    def time_settings(self, department=None):
        if department:
            return TimeGeneralSettings.objects.get(department=department)
        return TimeGeneralSettings.objects.get(department=self.department)

    def get_courses_queryset_by_parameters(
        self,
        period,
        flopmodel=None,
        train_prog=None,
        train_progs=None,
        group=None,
        groups=None,
        transversal_groups_included=False,
        module=None,
        modules=None,
        course_type=None,
        course_types=None,
        room_type=None,
        room_types=None,
    ):  # pylint: disable=too-many-arguments
        """
        Filter courses depending on constraints parameters
        parameter group : if not None, return all courses that has one group connected to group
        """
        if flopmodel is None:
            courses_qs = (
                Course.objects.filter(
                    period=period, groups__train_prog__department=self.department
                )
                .select_related("module", "type", "period")
                .prefetch_related("groups")
            )
        else:
            courses_qs = flopmodel.courses.filter(period=period)
        courses_filter = {}

        if train_prog is not None:
            courses_filter["module__train_prog"] = train_prog

        if train_progs:
            courses_filter["module__train_prog__in"] = train_progs

        if module is not None:
            courses_filter["module"] = module

        if modules:
            courses_filter["module__in"] = modules

        if group is not None:
            considered_groups = group.connected_groups()
            if transversal_groups_included:
                considered_groups |= group.transversal_conflicting_groups()
            courses_filter["groups__in"] = considered_groups

        if groups:
            all_groups = set()
            for g in groups:
                considered_groups = g.connected_groups()
                if transversal_groups_included:
                    considered_groups |= g.transversal_conflicting_groups()
                all_groups |= considered_groups
            courses_filter["groups__in"] = all_groups

        if course_type is not None:
            courses_filter["type"] = course_type

        if course_types:
            courses_filter["type__in"] = course_types

        if room_type is not None:
            courses_filter["room_type"] = room_type

        if room_types:
            courses_filter["room_type__in"] = room_types

        return courses_qs.filter(**courses_filter)

    def get_courses_queryset_by_attributes(self, period, flopmodel=None, **kwargs):
        """
        Filter courses depending constraint attributes
        """
        for attr_name in [
            "train_prog",
            "train_progs",
            "module",
            "modules",
            "group",
            "groups",
            "course_type",
            "course_types",
            "tutor",
            "tutors",
            "room_type",
            "room_types",
        ]:
            if hasattr(self, attr_name) and attr_name not in kwargs:
                attr = getattr(self, attr_name)
                if type(attr).__name__ == "ManyRelatedManager":
                    kwargs[attr_name] = attr.all()
                else:
                    kwargs[attr_name] = attr
        return self.get_courses_queryset_by_parameters(period, flopmodel, **kwargs)

    def considered_courses(self, period, flopmodel=None):
        return self.get_courses_queryset_by_attributes(period, flopmodel)

    def considered_train_progs(self, flopmodel=None):
        if flopmodel is None:
            train_progs = set(
                TrainingProgramme.objects.filter(department=self.department)
            )
        else:
            train_progs = set(flopmodel.train_prog)
        if hasattr(self, "train_progs"):
            if self.train_progs.exists():
                train_progs &= set(self.train_progs.all())
        return train_progs
