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

from base.models import UserAvailability, CourseAvailability

from base.models import TimeGeneralSettings
from base.timing import Time, days_index, Day, days_list
from base.models import ScheduledCourse

import datetime as dt

from base.timing import slot_pause

midday = dt.time(12, 0, 0)

basic_slot_duration = dt.timedelta(hours=1, minutes=30)


class Slot:
    def __init__(self, start_time: dt.datetime, end_time: dt.datetime, department=None):
        self.start_time = start_time
        self.end_time = end_time
        self.department=department

    @property
    def date(self):
        return self.start_time.date()
    
    @property
    def day(self):
        return self.date

    @property
    def duration(self):
        return self.end_time - self.start_time
    
    @property
    def minutes(self):
        return self.duration.seconds // 60

    @property
    def apm(self):
        pm_start = midday
        if self.start_time.time() >= pm_start:
            return Time.PM
        else:
            return Time.AM

    def __str__(self):
        return (f"{self.date} de {self.start_time.time()} à {self.end_time.time()}")

    def has_same_day(self, other):
        if isinstance(other, (Slot, CourseSlot, ScheduledCourse, UserAvailability, CourseAvailability)):         
            return self.date == other.date

        else:
            raise TypeError(
                "A slot can only have "
                "same day than a ScheduledCourse, UserAvailability, CourseAvailability or another slot"
            )

    def has_previous_day_than(self, other):
        if isinstance(other, (Slot, CourseSlot, ScheduledCourse, UserAvailability, CourseAvailability)):
            return self.date < other.date
        else:
            raise TypeError(
                "A slot can only have "
                "previous day than a ScheduledCourse, UserAvailability, CourseAvailability or another slot"
            )

    def is_simultaneous_to(self, other):
        return self.start_time < other.end_time and other.start_time < self.end_time

    def is_after(self, other):
        return self.start_time >= other.end_time

    def is_successor_of(self, other):
        other.end_time <= self.start_time <= other.end_time + slot_pause

    def __lt__(self, other):
        return other.is_after(self) and not self.is_after(other)

    def __repr__(self):
        return str(self)

    def get_day(self):
        return self.date
    
    def same_through_periods(self, other):
        if isinstance(other, (Slot, ScheduledCourse)):
            return self.date.weekday == other.date.weekday and self.start_time.time() == other.start_time.time() and self.duration == other.duration
        else:
            raise TypeError(
                "A slot can only be compared to another slot or a ScheduledCourse"
            )
    
    def get_periods(self):
        raise NotImplementedError


class CourseSlot(Slot):
    def __init__(self, start_time: dt.datetime, duration:dt.timedelta, department=None):
        Slot.__init__(self, start_time, start_time + duration, department)


    @property
    def apm(self):
        if self.department is not None:
            time = TimeGeneralSettings.objects.get(department=self.department)
            pm_start = time.afternoon_start_time
        else:
            pm_start = midday
        if self.start_time.time() >= pm_start:
            return Time.PM
        else:
            return Time.AM


    def __str__(self):
        hours = self.start_time.hour
        minuts = self.start_time.minute
        if minuts == 0:
            minuts = ""
        return (
            str(self.department)
            + "_"
            + str(self.start_time)
        )
    
    def get_periods(self):
        return self.department.periods()


def slots_filter(
    slot_set,
    day=None,
    apm=None,
    duration=None,
    start_time=None,
    weekday=None,
    weekday_in=None,
    simultaneous_to=None,
    period=None,
    is_after=None,
    starts_after=None,
    starts_before=None,
    ends_before=None,
    ends_after=None,
    day_in=None,
    same=None,
    period__in=None,
    department=None,
    date=None,
    date_in=None
):
    slots = slot_set
    if period is not None:
        slots = set(sl for sl in slots if period.start_date <= sl.date <= period.end_date)
    if period__in is not None:
        slots = set(sl for sl in slots if any(period.start_date <= sl.date <= period.end_date for period in period__in))
    if day is not None:
        slots = set(sl for sl in slots if sl.date == day)
    if day_in is not None:
        slots = set(sl for sl in slots if sl.date in day_in)
    if date is not None:
        slots = set(sl for sl in slots if sl.date == date)
    if date_in is not None:
        slots = set(sl for sl in slots if sl.date in date_in)
    if weekday is not None:
        slots = set(sl for sl in slots if days_list[sl.date.weekday()] == weekday)
    if weekday_in is not None:
        slots = set(sl for sl in slots if days_list[sl.date.weekday()] in weekday_in)
    if duration is not None:
        slots = set(sl for sl in slots if sl.duration == duration)
    if apm is not None:
        slots = set(sl for sl in slots if sl.apm == apm)
    if simultaneous_to is not None:
        slots = set(sl for sl in slots if sl.is_simultaneous_to(simultaneous_to))
    if is_after is not None:
        slots = set(sl for sl in slots if sl.is_after(is_after))
    if starts_after is not None:
        slots = set(sl for sl in slots if sl.start_time >= starts_after)
    if starts_before is not None:
        slots = set(sl for sl in slots if sl.start_time <= starts_before)
    if ends_before is not None:
        slots = set(sl for sl in slots if sl.end_time <= ends_before)
    if ends_after is not None:
        slots = set(sl for sl in slots if sl.end_time >= ends_after)
    if start_time is not None:
        slots = set(sl for sl in slots if sl.start_time == start_time)
    if same is not None:
        slots = set(sl for sl in slots if sl.same_through_periods(same))
    if department is not None:
        slots = set(sl for sl in slots if sl.department == department)
    return slots


def days_filter(
    days_set, index=None, index_in=None, period=None, period_in=None, weekday=None, weekday_in=None
):
    days = days_set
    if period is not None:
        days = set(d for d in days if period.start_date <= d <= period.end_date)
    if period_in is not None:
        days = set(d for d in days if any(period.start_date <= d <= period.end_date for period in period_in))
    if index is not None:
        days = set(d for d in days if d.weekday() == index)
    if index_in is not None:
        days = set(d for d in days if d.weekday() in index_in)
    if weekday is not None:
        days = set(d for d in days if days_list[d.weekday()] == weekday)
    if weekday_in is not None:
        days = set(d for d in days if days_list[d.weekday()] in weekday_in)
    return days


def corresponding_slot(scheduled_course):
    start_time = scheduled_course.start_time
    duration = scheduled_course.duration
    department = scheduled_course.course.type.department
    return CourseSlot(start_time, duration, department)
