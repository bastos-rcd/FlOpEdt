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

from TTapp.TTConstraints.TTConstraint import TTConstraint
from django.db import models
from base.timing import Day, TimeInterval, flopdate_to_datetime
from people.models import Tutor
from base.models import SchedulingPeriod
import datetime as dt

from TTapp.slots import slots_filter, days_filter

from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint
from .groups_constraints import considered_basic_groups
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class NoCourseOnWeekDay(TTConstraint):
    FULL_DAY = 'fd'
    AM = 'AM'
    PM = 'PM'
    PERIOD_CHOICES = ((FULL_DAY, _('Full day')), (AM, _('AM')), (PM, _('PM')))
    fampm_period = models.CharField(max_length=2, choices=PERIOD_CHOICES, verbose_name=_("fampm_period"))
    weekday = models.CharField(max_length=2, choices=Day.CHOICES)

    class Meta:
        abstract = True

    def considered_slots(self, ttmodel, period):
        if self.fampm_period == self.FULL_DAY:
            considered_slots = slots_filter(ttmodel.wdb.courses_slots,
                                            weekday=self.weekday, period=period)
        else:
            considered_slots = slots_filter(ttmodel.wdb.courses_slots,
                                            weekday=self.weekday, apm=self.fampm_period, period=period)
        return considered_slots

    def considered_sum(self, ttmodel, period):
        raise NotImplementedError

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        raise NotImplementedError
    
    def is_satisfied_for(self, period, work_copy):
        considered_scheduled_courses = self.period_work_copy_scheduled_courses_queryset(period, work_copy)
        # iso_week_day starts at 1 (for monday), so we need to add 1 to the rank
        iso_week_days_ranks = [rank + 1 for rank, day in enumerate(Day.CHOICES) if day[0] == self.weekday]
        if self.fampm_period == self.FULL_DAY:
            unwanted_considered_scheduled_courses = considered_scheduled_courses.filter(
                start_time__date__iso_week_day__in=iso_week_days_ranks)
        elif self.fampm_period == self.AM:
            unwanted_considered_scheduled_courses = considered_scheduled_courses.filter(
                start_time__date__iso_week_day__in=iso_week_days_ranks,
                start_time__time__lt=self.time_settings().morning_end_time)
        elif self.fampm_period == self.PM:
            unwanted_considered_scheduled_courses = considered_scheduled_courses.filter(
                start_time__date__iso_week_day__in=iso_week_days_ranks,
                start_time__time__gte=self.time_settings().afternoon_start_time)
        assert not unwanted_considered_scheduled_courses, f"Constraint {self} is not satisfied for period {period} and work_copy {work_copy} : {unwanted_considered_scheduled_courses}"
        


class NoGroupCourseOnWeekDay(NoCourseOnWeekDay):
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)
    groups = models.ManyToManyField('base.StructuralGroup', blank=True)
    course_types = models.ManyToManyField('base.CourseType', related_name='no_course_on_days', blank=True)
    transversal_groups_included = models.BooleanField(default=True, verbose_name=_("transveral_groups_included"))

    class Meta:
        verbose_name = _('No courses on declared week days for groups')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        if self.weight is None:
            ttmodel.add_constraint(self.considered_sum(ttmodel, period),
                                   '==', 0,
                                   Constraint(constraint_type=ConstraintType.NO_GROUP_COURSE_ON_WEEKDAY, periods=period,
                                              groups=considered_basic_groups(self, ttmodel)))
        else:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * self.considered_sum(ttmodel, period), period)

    def considered_courses(self, ttmodel):
        if self.transversal_groups_included:
            c_c = set(c for g in considered_basic_groups(self, ttmodel)
                      for c in ttmodel.wdb.all_courses_for_basic_group[g])
        else:
            c_c = set(c for g in considered_basic_groups(self, ttmodel)
                      for c in ttmodel.wdb.courses_for_basic_group[g])
        if self.course_types.exists():
            c_c = set(c for c in c_c
                      if c.type in self.course_types.all())
        return c_c

    def considered_sum(self, ttmodel, period):
        return ttmodel.sum(ttmodel.TT[(sl, c)]
                           for c in self.considered_courses(ttmodel)
                           for sl in self.considered_slots(ttmodel, period) & ttmodel.wdb.compatible_slots[c])

    def one_line_description(self):
        text = f"Aucun cours les {self.weekday}"
        if self.fampm_period != self.FULL_DAY:
            text += f" ({self.fampm_period})"
        if self.course_types.exists():
            text += f" pour les cours de type" + ', '.join([t.name for t in self.course_types.all()])
        if self.groups.exists():
            text += ' pour les groupes ' + ', '.join([group.name for group in self.groups.all()])
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        return text
    
    def get_slot_constraint(self, period, forbidden = False):
        time_settings = self.time_settings()
        if not self.periods.exists() or period in self.periods.all():
            days_break = days_filter(period.dates(), weekday=self.weekday)
            data = { "no_course_tutor" : 
                            { "tutors": self.groups.all(), "tutor_status": self.groups.all()}
                    }
            if forbidden:
                data["forbidden"] = True
            for day_break in days_break:
                if self.fampm_period == self.FULL_DAY:
                    data["no_course_tutor"]["period"] = {self.FULL_DAY}
                    return (TimeInterval(dt.datetime.combine(day_break, time_settings.day_start_time),
                                         dt.datetime.combine(day_break, time_settings.day_end_time)),
                            data)
                elif self.fampm_period == self.AM:
                    data["no_course_tutor"]["period"] = {self.AM}
                    return (TimeInterval(dt.datetime.combine(day_break, time_settings.day_start_time),
                                         dt.datetime.combine(day_break, time_settings.morning_end_time)),
                            data)
                elif self.fampm_period == self.PM:
                    data["no_course_tutor"]["period"] = {self.PM}
                    return (TimeInterval(dt.datetime.combine(day_break, time_settings.afternoon_start_time),
                                         dt.datetime.combine(day_break, time_settings.day_end_time)),
                            data)
        return None

    def complete_group_partition(self, partition, group, period):
        """
            Complete the partition in parameters with informations given by this NoGroupCourseOnDay constraint if it
        concern the given group and period.
        This method is called by functions in partition_with_constraints.py to initialize a partition used in pre_analyse methods.

        :param partition: A partition (empty or not) with informations about a group's availability.
        :type partition: Partition
        :param tutor: The group from whom the partition is about.
        :type tutor: StructuralGroup
        :param period: The SchedulingPeriod we want to make a pre-analysis on (can be None if all).
        :type period: SchedulingPeriod
        :return: A partition with new informations if the given tutor is concerned by this NoGroupCourseOnDay constraint.
        :rtype: Partition

        """
        if (not self.groups.exists() or group in self.groups.all()) \
                and (not self.periods.exists() or period in self.periods.all()):

            days_break = days_filter(period.dates(), weekday=self.weekday)
            time_settings = self.time_settings()
            for day_break in days_break:
                if self.fampm_period == self.FULL_DAY:
                    partition.add_slot(
                        TimeInterval(dt.datetime.combine(day_break, time_settings.day_start_time),
                                     dt.datetime.combine(day_break, time_settings.day_end_time)),
                        "forbidden",
                        {"value": 0, "forbidden": True, "group": group.name}
                    )
                elif self.fampm_period == self.AM:
                    partition.add_slot(
                        TimeInterval(dt.datetime.combine(day_break, time_settings.day_start_time),
                                     dt.datetime.combine(day_break, time_settings.morning_end_time)),
                        "forbidden",
                        {"value": 0, "forbidden": True, "group": group.name}
                    )

                elif self.fampm_period == self.PM:
                    partition.add_slot(
                        TimeInterval(dt.datetime.combine(day_break, time_settings.afternoon_start_time),
                                     dt.datetime.combine(day_break, time_settings.day_end_time)),
                        "forbidden",
                        {"value": 0, "forbidden": True, "group": group.name}
                    )

        return partition


class NoTutorCourseOnWeekDay(NoCourseOnWeekDay):
    train_progs = models.ManyToManyField('base.TrainingProgramme',
                                         blank=True)
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    tutor_status = models.CharField(max_length=2, choices=Tutor.TUTOR_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = _('No courses on declared days for tutors')
        verbose_name_plural = verbose_name

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        if self.weight is None:
            ttmodel.add_constraint(self.considered_sum(ttmodel, period),
                                   '==', 0,
                                   Constraint(constraint_type=ConstraintType.NO_TUTOR_COURSE_ON_DAY, periods=period,
                                              instructors=self.considered_tutors(ttmodel)))
        else:
            ttmodel.add_to_generic_cost(self.local_weight() * ponderation * self.considered_sum(ttmodel, period), period)

    def considered_tutors(self, ttmodel):
        if self.tutors.exists():
            tutors = set(t for t in ttmodel.wdb.instructors if t in self.tutors.all())
        else:
            tutors = set(ttmodel.wdb.instructors)
        if self.tutor_status is not None:
            tutors = set(t for t in tutors if t.status == self.tutor_status)
        return tutors

    def considered_sum(self, ttmodel, period):
        return ttmodel.sum(ttmodel.TTinstructors[(sl, c, i)]
                           for i in self.considered_tutors(ttmodel)
                           for c in ttmodel.wdb.possible_courses[i]
                           if c.module.train_prog in self.considered_train_progs(ttmodel)
                           for sl in self.considered_slots(ttmodel, period) & ttmodel.wdb.compatible_slots[c])

    def one_line_description(self):
        text = f"Aucun cours les {self.weekday}"
        if self.fampm_period != self.FULL_DAY:
            text += f" ({self.fampm_period})"
        if self.tutors.exists():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        if self.tutor_status is not None:
            text += f" (ne concerne que les {self.tutor_status} "
        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])
        return text

    def get_slot_constraint(self, period, forbidden = False):
        time_settings = self.time_settings()
        if not self.periods.exists() or period in self.periods.all():
            days_break = days_filter(period.dates(), weekday=self.weekday)
            data = { "no_course_tutor" : 
                            { "tutors": self.tutors.all(), "tutor_status": {self.tutor_status}  }
                    }
            if forbidden:
                data["forbidden"] = True
            for day_break in days_break:
                if self.fampm_period == self.FULL_DAY:
                    data["no_course_tutor"]["period"] = {self.FULL_DAY}
                    return (TimeInterval(dt.datetime.combine(day_break, time_settings.day_start_time),
                                         dt.datetime.combine(day_break, time_settings.day_finish_time)),
                            data)
                elif self.fampm_period == self.AM:
                    data["no_course_tutor"]["period"] = {self.AM}
                    return (TimeInterval(dt.datetime.combine(day_break, time_settings.day_start_time),
                                         dt.datetime.combine(day_break, time_settings.morning_end_time)),
                            data)
                elif self.fampm_period == self.PM:
                    data["no_course_tutor"]["period"] = {self.PM}
                    return (TimeInterval(dt.datetime.combine(day_break, time_settings.afternoon_start_time),
                                         dt.datetime.combine(day_break, time_settings.day_end_time)),
                            data)
        return None


    @staticmethod
    def tutor_and_supp(interval, required_supps, possible_tutors):
        """Looking in the interval if all required_supp and at least one possible_tutors are available
        in the user preferences and not in the no course key.
        Complexity on O(t*t') with t being the number of tutors in required supp and possible_tutors and t'
        then number of tutors in the 'user_preference' key of the interval data.

        Parameters:
            interval (tuple(TimeInterval, dict)): A partition interval
            required_supps (list(Tutor)): A list of required tutors for that course
            possible_tutors (list(Tutor)): A list of tutors available for the course
            
        Returns:
            (boolean): Whether or not all supp_tutors and one possible_tutor are ready"""
        supp_in = 0
        tutor_in = possible_tutors == []
        if "user_preference" in interval[1]:
            for tutor, value in interval[1]["user_preference"].items():
                if tutor in required_supps and value > 0:
                    if ("no_course_tutor" not in interval[1]
                        or (tutor not in interval[1]["no_course_tutor"]["tutors"]
                            and tutor.status not in interval[1]["no_course_tutor"]["tutor_status"])):
                        supp_in += 1
                if tutor in possible_tutors and value > 0:
                    tutor_in = (tutor_in
                        or "no_course_tutor" not in interval[1]
                        or tutor not in interval[1]["no_course_tutor"]["tutors"]
                            and tutor.status not in interval[1]["no_course_tutor"]["tutor_status"])
                if supp_in == len(required_supps) and tutor_in:
                    break
        return supp_in == len(required_supps) and tutor_in

    def complete_tutor_partition(self, partition, tutor, period):
        """
            Complete the partition in parameters with informations given by this NoTutorCourseOnDay constraint if it
        concern the given tutor and period.
        This method is called by functions in partition_with_constraints.py to initialize a partition used in pre_analyse methods.

        :param partition: A partition (empty or not) with informations about a tutor's availability.
        :type partition: Partition
        :param tutor: The tutor from whom the partition is about.
        :type tutor: Tutor
        :param period: The SchedulingPeriod we want to make a pre-analysis on (can be None if all).
        :type week: SchedulingPeriod
        :return: A partition with new informations if the given tutor is concerned by this NoTutorCourseOnDay constraint.
        :rtype: Partition

        """
        
        if (not self.tutors.exists() or tutor in self.tutors.all()) \
                and (not self.periods.exists() or period in self.periods.all()):
            days_break = days_filter(period.dates(), weekday=self.weekday)
            time_settings = self.time_settings()
            for day_break in days_break:
                if self.fampm_period == self.FULL_DAY:
                    partition.add_slot(
                        TimeInterval(dt.datetime.combine(day_break, time_settings.day_start_time),
                                     dt.datetime.combine(day_break, time_settings.day_end_time)),
                        "forbidden",
                        {"value": 0, "forbidden": True, "tutor": tutor.username}
                    )
                elif self.fampm_period == self.AM:
                    partition.add_slot(
                        TimeInterval(dt.datetime.combine(day_break, time_settings.day_start_time),
                                     dt.datetime.combine(day_break, time_settings.morning_end_time)),
                        "forbidden",
                        {"value": 0, "forbidden": True, "tutor": tutor.username}
                    )

                elif self.fampm_period == self.PM:
                    partition.add_slot(
                        TimeInterval(dt.datetime.combine(day_break, time_settings.afternoon_start_time),
                                     dt.datetime.combine(day_break, time_settings.day_end_time)),
                        "forbidden",
                        {"value": 0, "forbidden": True, "tutor": tutor.username}
                    )

        return partition
