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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from base.models import ScheduledCourse
from base.timing import Day, TimeInterval
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.slots import Slot, days_filter, slots_filter
from TTapp.TimetableConstraints.timetable_constraint import TimetableConstraint
from TTapp.TimetableConstraints.tutors_constraints import considered_tutors


class GroupsLunchBreak(TimetableConstraint):
    """
    Ensures time for lunch in a given interval for given groups (all if groups is Null)
    """

    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    start_lunch_time = models.TimeField()
    end_lunch_time = models.TimeField()
    # ArrayField unusable with django-import-export
    weekdays = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True
    )
    lunch_length = models.DurationField()
    groups = models.ManyToManyField(
        "base.StructuralGroup", blank=True, related_name="lunch_breaks_constraints"
    )

    class Meta:
        verbose_name = _("Lunch break for groups")
        verbose_name_plural = verbose_name

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(["train_progs", "groups"])
        return attributes

    def enrich_ttmodel(self, ttmodel, period, ponderation=100):
        considered_groups = self.considered_basic_groups(ttmodel)
        days = days_filter(ttmodel.data.days, period=period)
        if self.weekdays:
            days = days_filter(days, weekday_in=self.weekdays)
        for day in days:
            day_lunch_start_time = dt.datetime.combine(day, self.start_lunch_time)
            local_slots = []
            slot_start_time = day_lunch_start_time
            slot_end_time = slot_start_time + self.lunch_length
            while slot_end_time <= dt.datetime.combine(day, self.end_lunch_time):
                local_slots.append(Slot(slot_start_time, slot_end_time))
                slot_start_time += dt.timedelta(minutes=15)
                slot_end_time += dt.timedelta(minutes=15)
            slots_nb = len(local_slots)
            # pour chaque groupe, au moins un de ces slots ne voit aucun cours lui être simultané
            slot_vars = {}

            for group in considered_groups:
                considered_courses = self.get_courses_queryset_by_parameters(
                    period, ttmodel, group=group
                )
                for local_slot in local_slots:
                    # Je veux que slot_vars[group, local_slot] soit à 1
                    # si et seulement si undesired_scheduled_courses vaut plus que 1
                    undesired_scheduled_courses = ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for c in considered_courses
                        for sl in slots_filter(
                            ttmodel.data.compatible_slots[c], simultaneous_to=local_slot
                        )
                    )
                    slot_vars[group, local_slot] = ttmodel.add_floor(
                        expr=undesired_scheduled_courses,
                        floor=1,
                        bound=len(considered_courses),
                    )
                not_ok = ttmodel.add_floor(
                    expr=ttmodel.sum(slot_vars[group, sl] for sl in local_slots),
                    floor=slots_nb,
                    bound=2 * slots_nb,
                )

                if self.weight is None:
                    ttmodel.add_constraint(
                        not_ok,
                        "==",
                        0,
                        Constraint(ConstraintType.GROUPS_LUNCH_BREAK, groups=group),
                    )

                else:
                    cost = not_ok * ponderation * self.local_weight()
                    # cost = ttmodel.sum(slot_vars[group, sl] for sl in local_slots) * ponderation \
                    #        * self.local_weight()
                    ttmodel.add_to_group_cost(group, cost, period)

    def is_satisfied_for(self, period, version):
        """
        Check if the constraint is satisfied for a given period and version.
        """
        considered_scheduled_courses = self.period_version_scheduled_courses_queryset(
            period, version
        )
        considered_dates = period.dates()
        if self.weekdays:
            considered_dates = days_filter(considered_dates, weekday_in=self.weekdays)
        no_lunch_dates = []
        for basic_group in self.considered_basic_groups():
            group_considered_scheduled_courses = considered_scheduled_courses.filter(
                course__groups__in=basic_group.and_ancestors()
            )
            for date in considered_dates:
                is_ok = False
                start_time = dt.datetime.combine(date, self.start_lunch_time)
                lunch_end_time = dt.datetime.combine(date, self.end_lunch_time)
                is_ok = False
                while start_time <= lunch_end_time - self.lunch_length:
                    end_time = start_time + self.lunch_length
                    if not any(
                        sc.start_time < end_time and sc.end_time > start_time
                        for sc in group_considered_scheduled_courses
                    ):
                        is_ok = True
                        break
                    start_time += dt.timedelta(minutes=15)
                if not is_ok:
                    no_lunch_dates.append((date, basic_group))
        assert not no_lunch_dates, f"No lunch break for groups {no_lunch_dates}"

    def one_line_description(self):
        text = (
            f"Il faut une pause déjeuner d'au moins {self.lunch_length} minutes "
            f"entre {self.start_lunch_time} et {self.end_lunch_time}"
        )
        try:
            text += " les " + ", ".join(
                [wd for wd in self.weekdays]
            )  # pylint: disable=unnecessary-comprehension
        except ObjectDoesNotExist:
            pass
        if self.groups.exists():
            text += " pour les groupes " + ", ".join(
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

    def complete_group_partition(self, partition, group, period):
        """
            Complete the partition in parameters with informations
            given by this GroupLunchBreak constraint if it concerns the given group and period.
            This method is called by functions in partition_with_constraints.py
            to initialize a partition used in pre_analyse methods.

        :param partition: A partition (empty or not) with informations about a group's availability.
        :type partition: Partition
        :param tutor: The group from whom the partition is about.
        :type tutor: StructuralGroup
        :param period: The SchedulingPeriod we want to make a pre-analysis on (can be None if all).
        :type week: SchedulingPeriod
        :return: A partition with new informations if the given tutor is concerned
        by this GroupLunchBreak constraint.
        :rtype: Partition

        """

        if (not self.groups.exists() or group in self.groups.all()) and (
            not self.periods.exists() or period in self.periods.all()
        ):
            days = period.dates()
            if self.weekdays:
                days = days_filter(days, weekday_in=self.weekdays)
            for day in days:
                max_lunch_start_time = (
                    dt.datetime.combine(day, self.end_lunch_time) - self.lunch_length
                )
                partition.add_slot(
                    TimeInterval(
                        max_lunch_start_time,  # dt.datetime.combine(day, self.start_lunch_time),
                        dt.datetime.combine(day, self.end_lunch_time),
                    ),
                    "forbidden",
                    {"value": 0, "forbidden": True, "group_lunch_break": group.name},
                )

        return partition


class TutorsLunchBreak(TimetableConstraint):
    """
    Ensures time for lunch in a given interval for given tutors (all if tutors is Null)
    """

    start_lunch_time = models.TimeField(help_text=_("start lunch time"))
    end_lunch_time = models.TimeField(help_text=_("end lunch time"))
    weekdays = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES),
        blank=True,
        null=True,
        help_text=_("considered week days"),
    )
    lunch_length = models.DurationField(help_text=_("minimal lunch length"))
    tutors = models.ManyToManyField(
        "people.Tutor",
        blank=True,
        related_name="lunch_breaks_constraints",
        help_text=_("considered tutors"),
    )

    class Meta:
        verbose_name = _("Lunch break for tutors")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=100):
        tutors_to_be_considered = considered_tutors(self, ttmodel)
        if self.tutors.exists():
            tutors_to_be_considered &= set(self.tutors.all())
        days = days_filter(ttmodel.data.days, period=period)
        if self.weekdays:
            days = days_filter(days, weekday_in=self.weekdays)
        for day in days:
            day_lunch_start_time = dt.datetime.combine(day, self.start_lunch_time)
            local_slots = []
            slot_start_time = day_lunch_start_time
            slot_end_time = slot_start_time + self.lunch_length
            while slot_end_time <= dt.datetime.combine(day, self.end_lunch_time):
                local_slots.append(Slot(slot_start_time, slot_end_time))
                slot_start_time += dt.timedelta(minutes=15)
                slot_end_time += dt.timedelta(minutes=15)
            slots_nb = len(local_slots)
            # pour chaque prof, au moins un de ces slots ne voit aucun cours lui être simultané
            for tutor in tutors_to_be_considered:
                slot_vars = {}
                other_deps_unavailable_slots_number = 0
                considered_courses = self.get_courses_queryset_by_parameters(
                    period, ttmodel, tutor=tutor
                )
                if not considered_courses:
                    continue
                other_dep_scheduled_courses = set(
                    ttmodel.data.other_departments_scheduled_courses_for_tutor[tutor]
                ) | set(
                    ttmodel.data.other_departments_scheduled_courses_for_supp_tutor[
                        tutor
                    ]
                )
                for local_slot in local_slots:
                    # Je veux que slot_vars[tutor, local_slot] soit à 1
                    # si et seulement si
                    # undesired_scheduled_courses ou other_dep_undesired_sc_nb vaut plus que 1
                    considered_sl_c = set(
                        (sl, c)
                        for c in considered_courses
                        for sl in slots_filter(
                            ttmodel.data.compatible_slots[c], simultaneous_to=local_slot
                        )
                    )
                    if not considered_sl_c:
                        continue
                    undesired_scheduled_courses = ttmodel.sum(
                        ttmodel.assigned[sl, c, tutor] for (sl, c) in considered_sl_c
                    )
                    if not other_dep_scheduled_courses:
                        other_dep_undesired_sc_nb = 0
                    else:
                        other_dep_undesired_scheduled_courses = set(
                            sc
                            for sc in other_dep_scheduled_courses
                            if (
                                sc.start_time < local_slot.end_time
                                and local_slot.start_time < sc.end_time
                            )
                        )
                        other_dep_undesired_sc_nb = len(
                            other_dep_undesired_scheduled_courses
                        )
                        if other_dep_undesired_sc_nb:
                            other_deps_unavailable_slots_number += 1
                    undesired_expression = (
                        undesired_scheduled_courses
                        + other_dep_undesired_sc_nb * ttmodel.one_var
                    )
                    slot_vars[local_slot] = ttmodel.add_floor(
                        expr=undesired_expression,
                        floor=1,
                        bound=len(considered_courses),
                    )
                if not slot_vars:
                    continue

                if other_deps_unavailable_slots_number == slots_nb:
                    ttmodel.add_warning(
                        tutor,
                        _(f"Not able to eat in other departments on {day}-{period}"),
                    )
                    continue
                not_ok = ttmodel.add_floor(
                    expr=ttmodel.sum(slot_vars.values()),
                    floor=slots_nb,
                    bound=2 * slots_nb,
                )

                if self.weight is None:
                    ttmodel.add_constraint(
                        not_ok,
                        "==",
                        0,
                        Constraint(
                            ConstraintType.TUTORS_LUNCH_BREAK, instructors=tutor
                        ),
                    )

                else:
                    cost = not_ok * ponderation * self.local_weight()
                    ttmodel.add_to_inst_cost(tutor, cost, period)

    def is_satisfied_for(self, period, version):
        """
        Check if the constraint is satisfied for a given period and version.
        """
        considered_scheduled_courses = self.period_version_scheduled_courses_queryset(
            period, version
        )
        considered_dates = period.dates()
        if self.weekdays:
            considered_dates = days_filter(considered_dates, weekday_in=self.weekdays)
        no_lunch_dates = []
        tutors_to_consider = set(
            sc.tutor for sc in considered_scheduled_courses.distinct("tutor")
        )
        if self.tutors.exists():
            tutors_to_consider &= set(self.tutors.all())
        for tutor in tutors_to_consider:
            tutor_considered_scheduled_courses = considered_scheduled_courses.filter(
                tutor=tutor
            )
            for date in considered_dates:
                start_time = dt.datetime.combine(date, self.start_lunch_time)
                lunch_end_time = dt.datetime.combine(date, self.end_lunch_time)
                is_ok = False
                while start_time <= lunch_end_time - self.lunch_length:
                    end_time = start_time + self.lunch_length
                    if not any(
                        sc.start_time < end_time and sc.end_time > start_time
                        for sc in tutor_considered_scheduled_courses
                    ):
                        is_ok = True
                        break
                    start_time += dt.timedelta(minutes=15)
                if not is_ok:
                    no_lunch_dates.append((date, tutor))
        assert not no_lunch_dates, f"No lunch break for tutors on {no_lunch_dates}"

    def complete_tutor_partition(self, partition, tutor, period):
        """
            Complete the partition in parameters with informations
            given by this TutorsLunchBreak constraint if it concerns the given tutor and period.
            This method is called by functions in partition_with_constraints.py
            to initialize a partition used in pre_analyse methods.

        :param partition: A partition (empty or not) with informations about a tutor's availability.
        :type partition: Partition
        :param tutor: The tutor from whom the partition is about.
        :type tutor: Tutor
        :param period: The SchedulingPeriod we want to make a pre-analysis on (can be None if all).
        :type period: SchedulingPeriod
        :return: A partition with new informations if the given tutor is concerned
        by this TutorsLunchBreak constraint.
        :rtype: Partition

        """

        if (not self.tutors.exists() or tutor in self.tutors.all()) and (
            not self.periods.exists() or period in self.periods.all()
        ):
            days = period.dates()
            if self.weekdays:
                days = days_filter(days, weekday_in=self.weekdays)
            for day in days:
                max_lunch_start_time = (
                    dt.datetime.combine(day, self.end_lunch_time) - self.lunch_length
                )
                partition.add_slot(
                    TimeInterval(
                        max_lunch_start_time,  # dt.datetime.combine(day, self.start_lunch_time),
                        dt.datetime.combine(day, self.end_lunch_time),
                    ),
                    "forbidden",
                    {
                        "value": 0,
                        "forbidden": True,
                        "tutor_lunch_break": tutor.username,
                    },
                )

        return partition

    def one_line_description(self):
        text = (
            f"Il faut une pause déjeuner d'au moins {self.lunch_length} minutes "
            f"entre {self.start_lunch_time} et {self.end_lunch_time}"
        )
        try:
            text += " les " + ", ".join([wd for wd in self.weekdays])
        except ObjectDoesNotExist:
            pass
        if self.tutors.exists():
            text += " pour " + ", ".join(
                [tutor.username for tutor in self.tutors.all()]
            )
        else:
            text += " pour tous les profs."
        return text


class BreakAroundCourseType(TimetableConstraint):
    """
    Ensures that the courses of a given course type and other types of courses cannot be consecutive for the given groups.
    """

    weekdays = ArrayField(
        models.CharField(max_length=2, choices=Day.CHOICES), blank=True, null=True
    )
    groups = models.ManyToManyField(
        "base.StructuralGroup", blank=True, related_name="amphi_break_constraint"
    )
    train_progs = models.ManyToManyField("base.TrainingProgramme", blank=True)
    course_type = models.ForeignKey(
        "base.CourseType",
        related_name="amphi_break_constraint",
        on_delete=models.CASCADE,
    )
    min_break_after = models.DurationField(
        default=dt.timedelta(minutes=15), null=True, blank=True
    )
    min_break_before = models.DurationField(
        default=dt.timedelta(minutes=15), null=True, blank=True
    )

    class Meta:
        verbose_name = _("A break around some type courses")
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1000):
        considered_groups = self.considered_basic_groups(ttmodel)
        days = days_filter(ttmodel.data.days, period=period)
        if self.weekdays:
            days = days_filter(days, weekday_in=self.weekdays)
        for group in considered_groups:
            specific_courses = set(
                self.get_courses_queryset_by_parameters(
                    period, ttmodel, group=group, course_type=self.course_type
                )
            )
            all_courses = set(
                self.get_courses_queryset_by_parameters(period, ttmodel, group=group)
            )
            broken_breaks = ttmodel.lin_expr()
            for day in days:
                day_slots = slots_filter(ttmodel.data.courses_slots, day=day)
                for slot1 in day_slots:
                    successive_slots = set(
                        sl
                        for sl in day_slots
                        if slot1.end_time
                        <= sl.start_time
                        < slot1.end_time + self.min_break_after
                    )
                    if not successive_slots:
                        continue
                    amphi_slot = ttmodel.sum(
                        ttmodel.scheduled[slot1, c]
                        for c in specific_courses
                        & ttmodel.data.compatible_courses[slot1]
                    )
                    other_slot = ttmodel.sum(
                        ttmodel.scheduled[slot2, c]
                        for slot2 in successive_slots
                        for c in all_courses & ttmodel.data.compatible_courses[slot2]
                    )
                    broken_breaks += ttmodel.add_floor(
                        expr=amphi_slot + other_slot, floor=2, bound=2
                    )
                for slot1 in day_slots:
                    previous_slots = set(
                        sl
                        for sl in day_slots
                        if slot1.start_time - self.min_break_before
                        < sl.end_time
                        <= slot1.start_time
                    )
                    if not previous_slots:
                        continue
                    amphi_slot = ttmodel.sum(
                        ttmodel.scheduled[slot1, c]
                        for c in specific_courses
                        & ttmodel.data.compatible_courses[slot1]
                    )
                    other_slot = ttmodel.sum(
                        ttmodel.scheduled[slot2, c]
                        for slot2 in previous_slots
                        for c in all_courses & ttmodel.data.compatible_courses[slot2]
                    )
                    broken_breaks += ttmodel.add_floor(
                        expr=amphi_slot + other_slot, floor=2, bound=2
                    )

            if self.weight is None:
                ttmodel.add_constraint(
                    broken_breaks,
                    "==",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.BREAK_AROUND_COURSE, groups=group
                    ),
                )
            else:
                cost = broken_breaks * ponderation * self.local_weight()
                ttmodel.add_to_group_cost(group, cost, period)

    def is_satisfied_for(self, period, version):
        considered_groups = self.considered_groups(transversal_groups_included=True)
        considered_dates = period.dates()
        if self.weekdays:
            considered_dates = days_filter(considered_dates, weekday_in=self.weekdays)
        all_scheduled_courses = ScheduledCourse.objects.filter(
            course__type__department=self.department,
            course__period=period,
            start_time__date__in=considered_dates,
            version=version,
            course__groups__in=considered_groups,
        )
        course_type_scheduled_courses = all_scheduled_courses.filter(
            course__type=self.course_type
        )
        no_break_after_courses = set()
        no_break_before_courses = set()
        for sched_course in course_type_scheduled_courses:
            if all_scheduled_courses.filter(
                start_time__lt=sched_course.end_time + self.min_break_after,
                start_time__gte=sched_course.end_time,
            ).exists():
                no_break_after_courses.add(sched_course)
            if all_scheduled_courses.filter(
                start_time__gt=sched_course.start_time
                - self.min_break_before
                - F("course__duration"),
                start_time__lte=sched_course.start_time - F("course__duration"),
            ).exists():
                no_break_before_courses.add(sched_course)
        assert (
            not no_break_after_courses and not no_break_before_courses
        ), f"Break around course type {self.course_type} not respected for {no_break_after_courses | no_break_before_courses}."

    def one_line_description(self):
        text = (
            f"Il faut une pause "
            f"entre un cours de type {self.course_type.name} et un autre type de cours"
        )
        try:
            text += " les " + ", ".join([wd for wd in self.weekdays])
        except ObjectDoesNotExist:
            pass
        if self.groups.exists():
            text += " pour les groupes " + ", ".join(
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
