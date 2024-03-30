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

import datetime as dt

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.timing import Day, Time
from base.models import ScheduledCourse
from people.models import GroupPreferences
from TTapp.helpers.minhalfdays import MinHalfDaysHelperGroup
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.slots import days_filter, slots_filter
from TTapp.TimetableConstraints.timetable_constraint import TimetableConstraint


class MinGroupsHalfDays(TimetableConstraint):
    """
    All courses will fit in a minimum of half days
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)

    class Meta:
        verbose_name = _("Minimize busy half-days for groups")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        helper = MinHalfDaysHelperGroup(ttmodel, self, period, ponderation)
        for group in self.considered_basic_groups(ttmodel):
            helper.enrich_model(group=group)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model["details"]

        if self.groups.exists():
            details.update(
                {"groups": ", ".join([group.name for group in self.groups.all()])}
            )

        return view_model

    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.groups.exists():
            text += " des groupes " + ", ".join(
                [group.name for group in self.groups.all()]
            )
        else:
            text += " de tous les groupes"

        if self.train_progs.exists():
            text += " de " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " de toutes les promos."

        return text

    def __str__(self):
        return _("Minimize groups half-days")

    def is_satisfied_for(self, period, version):
        unsatisfied_min_half_days_groups = []
        for basic_group in self.considered_basic_groups():
            considered_courses = self.get_courses_queryset_by_parameters(
                period=period, group=basic_group
            )
            considered_scheduled_courses = ScheduledCourse.objects.filter(
                course__in=considered_courses, version=version
            )
            limit = MinHalfDaysHelperGroup.minimal_half_days_number(considered_courses)
            busy_half_days = sum(
                1
                for date in period.dates()
                for apm in [Time.AM, Time.PM]
                if set(
                    sched_course
                    for sched_course in considered_scheduled_courses.filter(date=date)
                    if sched_course.apm == apm
                )
            )
            if busy_half_days > limit:
                unsatisfied_min_half_days_groups.append(basic_group)
        assert (
            not unsatisfied_min_half_days_groups
        ), f"Unsatisfied min half days groups: {unsatisfied_min_half_days_groups}"


class MinNonPreferedTrainProgsSlot(TimetableConstraint):
    """
    Minimize the use of unprefered Slots for groups.
    Make impossible the use of forbidden slots.
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)

    class Meta:
        verbose_name = _("Minimize undesired slots for groups")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=None):
        if ponderation is None:
            ponderation = ttmodel.min_ups_c
        if self.train_progs.exists():
            train_progs = set(
                tp for tp in self.train_progs.all() if tp in ttmodel.train_prog
            )
        else:
            train_progs = set(ttmodel.train_prog)
        for train_prog in train_progs:
            basic_groups = ttmodel.data.basic_groups.filter(train_prog=train_prog)
            for g in basic_groups:
                g_pref, _ = GroupPreferences.objects.get_or_create(group=g)
                g_pref.calculate_fields()
                morning_weight = 2 * g_pref.get_morning_weight()
                evening_weight = 2 * g_pref.get_evening_weight()
                light_day_weight = 2 * g_pref.get_light_day_weight()
                for sl in ttmodel.data.availability_slots:
                    day_time_ponderation = light_day_weight
                    if sl in ttmodel.data.first_hour_slots:
                        day_time_ponderation *= morning_weight
                    elif sl in ttmodel.data.last_hour_slots:
                        day_time_ponderation *= evening_weight

                    for c in ttmodel.data.courses_for_basic_group[g]:
                        slot_vars_sum = ttmodel.sum(
                            ttmodel.scheduled[(sl2, c)]
                            for sl2 in slots_filter(
                                ttmodel.data.compatible_slots[c], simultaneous_to=sl
                            )
                        )
                        cost = (
                            self.local_weight()
                            * ponderation
                            * slot_vars_sum
                            * ttmodel.unp_slot_cost_course[c.type, train_prog][sl]
                        )
                        cost *= day_time_ponderation + 1
                        ttmodel.add_to_group_cost(g, cost, period=period)

            if self.weight is None:
                for course_type in ttmodel.data.course_types:
                    for sl in ttmodel.data.availability_slots:
                        if ttmodel.avail_course[(course_type, train_prog)][sl] == 0:
                            ttmodel.add_constraint(
                                ttmodel.sum(
                                    ttmodel.scheduled[(sl2, c)]
                                    for g in basic_groups
                                    for c in ttmodel.data.courses_for_basic_group[g]
                                    for sl2 in slots_filter(
                                        ttmodel.data.compatible_slots[c],
                                        simultaneous_to=sl,
                                    )
                                ),
                                "==",
                                0,
                                Constraint(
                                    constraint_type=ConstraintType.TRAIN_PROG_FORBIDDEN_SLOT,
                                    slots=sl,
                                ),
                            )

    def one_line_description(self):
        text = "Respecte les préférences"
        if self.train_progs.exists():
            text += " des groupes de " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " de toutes les promos."
        return text

    def __str__(self):
        return _("Minimize groups non-preferred slots")

    def is_satisfied_for(self, period, version):
        raise NotImplementedError


class GroupsMinHoursPerDay(TimetableConstraint):
    """
    Respect the min_time_per_day declared
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    groups = models.ManyToManyField("base.StructuralGroup", blank=True)
    min_time = models.DurationField(
        default=dt.timedelta(hours=3), verbose_name=_("min_time")
    )
    weekdays = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Respect groups min time per day bounds")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        """
        avoid situations in which a teaching day has less hours than time
        """
        considered_groups = self.considered_basic_groups(ttmodel)

        min_time = self.min_time
        if not min_time:
            return

        days = days_filter(ttmodel.data.days, period=period)
        if self.weekdays:
            days = days_filter(days, weekday_in=self.weekdays)
        for basic_group in considered_groups:
            for day in days:
                group_day_scheduled_minutes = ttmodel.sum(
                    ttmodel.scheduled[sl, c] * sl.minutes
                    for c in ttmodel.data.courses_for_basic_group[basic_group]
                    for sl in slots_filter(ttmodel.data.compatible_slots[c], day=day)
                )
                has_enough_time = ttmodel.add_floor(
                    group_day_scheduled_minutes, min_time.seconds // 60, 100000
                )
                undesired_situation = (
                    ttmodel.group_busy_day[(basic_group, day)] - has_enough_time
                )
                if self.weight is None:
                    ttmodel.add_constraint(
                        undesired_situation,
                        "==",
                        0,
                        Constraint(
                            constraint_type=ConstraintType.MIN_HOURS_PER_DAY,
                            groups=basic_group,
                            days=day,
                        ),
                    )
                else:
                    ttmodel.add_to_group_cost(
                        basic_group,
                        self.local_weight() * ponderation * undesired_situation,
                        period=period,
                    )

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model["details"]

        if self.groups.exists():
            details.update(
                {"groups": ", ".join([group.full_name for group in self.groups.all()])}
            )
        else:
            details.update({"groups": "All"})
        return view_model

    def one_line_description(self):
        """
        You can give a contextual explanation about what this constraint doesnt
        """
        return "Groups min hours per day"

    def is_satisfied_for(self, period, version):
        raise NotImplementedError
