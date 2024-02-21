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
from base.timing import Time, days_index, Day
from base.models import ScheduledCourse

slot_pause = 30

midday = 12 * 60

basic_slot_duration = 90


class Slot:
    def __init__(self, day, start_time, end_time):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def apm(self):
        pm_start = midday
        if self.start_time >= pm_start:
            return Time.PM
        else:
            return Time.AM

    def __str__(self):
        return (f"{self.day} de {self.start_time} à {self.end_time}")

    def has_same_day(self, other):
        if isinstance(other, (Slot, CourseSlot)):
            return self.day.equals(other.day)
        elif isinstance(other, ScheduledCourse):
            return self.day.week == other.course.week and self.day.day == other.day
        elif isinstance(other, (UserAvailability, CourseAvailability)):
            return self.day.week == other.week and self.day.day == other.day
        else:
            raise TypeError(
                "A slot can only have "
                "same day than a ScheduledCourse, UserAvailability, CourseAvailability or another slot"
            )

    def has_previous_day_than(self, other):
        if isinstance(other, (Slot, CourseSlot)):
            return (
                self.day.week < other.day.week
                or self.day.week == other.day.week
                and days_index[self.day.day] < days_index[other.day.day]
            )
        elif isinstance(other, ScheduledCourse):
            return (
                self.day.week < other.course.week
                or self.day.week == other.course.week
                and days_index[self.day.day] < days_index[other.day]
            )
        elif isinstance(other, (UserAvailability, CourseAvailability)):
            return (
                self.day.week < other.week
                or self.day.week == other.week
                and days_index[self.day.day] < days_index[other.day]
            )
        else:
            raise TypeError(
                "A slot can only have "
                "previous day than a ScheduledCourse, UserAvailability, CourseAvailability or another slot"
            )

    def is_simultaneous_to(self, other):
        if (
            self.has_same_day(other)
            and self.start_time < other.end_time
            and other.start_time < self.end_time
        ):
            return True
        else:
            return False

    def is_after(self, other):
        if (
            other.has_previous_day_than(self)
            or self.has_same_day(other)
            and self.start_time >= other.end_time
        ):
            return True
        else:
            return False

    def is_successor_of(self, other):
        return (
            self.has_same_day(other)
            and other.end_time <= self.start_time <= other.end_time + slot_pause
        )

    def __lt__(self, other):
        return other.is_after(self) and not self.is_after(other)

    def __repr__(self):
        return str(self)

    def get_day(self):
        return self.day

    def same_through_weeks(self, other):
        if isinstance(other, (Slot, CourseSlot)):
            return (
                self.day.day == other.day.day
                and self.start_time == other.start_time
                and self.end_time == other.end_time
            )
        elif isinstance(other, (ScheduledCourse, UserAvailability)):
            return (
                self.day.day == other.day
                and self.start_time == other.start_time
                and self.end_time == other.end_time
            )


class CourseSlot(Slot):
    def __init__(self, day, start_time, duration, department=None):
        Slot.__init__(self, day, start_time, start_time + duration)
        self.department=department


    @property
    def apm(self):
        if self.department is not None:
            time = TimeGeneralSettings.objects.get(department=self.department)
            pm_start = time.afternoon_start_time
        else:
            pm_start = midday
        if self.start_time >= pm_start:
            return Time.PM
        else:
            return Time.AM

    def same_through_weeks(self, other):
        return (
            self.day.day == other.day.day
            and self.start_time == other.start_time
        )


    def __str__(self):
        hours = self.start_time // 60
        minuts = self.start_time % 60
        if minuts == 0:
            minuts = ""
        return (
            str(self.department)
            + "_"
            + str(self.day)
            + "_"
            + str(hours)
            + "h"
            + str(minuts)
        )


def slots_filter(
    slot_set,
    day=None,
    apm=None,
    duration=None,
    start_time=None,
    week_day=None,
    simultaneous_to=None,
    week=None,
    is_after=None,
    starts_after=None,
    starts_before=None,
    ends_before=None,
    ends_after=None,
    day_in=None,
    same=None,
    week_in=None,
    department=None
):
    slots = slot_set
    if week is not None:
        slots = set(sl for sl in slots if sl.day.week == week)
    if week_in is not None:
        slots = set(sl for sl in slots if sl.day.week in week_in)
    if day is not None:
        slots = set(sl for sl in slots if sl.day.equals(day))
    if day_in is not None:
        slots = set(sl for sl in slots if sl.day in day_in)
    if week_day is not None:
        slots = set(sl for sl in slots if sl.day.day == week_day)
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
        slots = set(sl for sl in slots if sl.same_through_weeks(same))
    if department is not None:
        slots = set(sl for sl in slots if sl.department == department)
    return slots


def days_filter(
    days_set, index=None, index_in=None, week=None, week_in=None, day=None, day_in=None
):
    days = days_set
    if week is not None:
        days = set(d for d in days if d.week == week)
    if week_in is not None:
        days = set(d for d in days if d.week in week_in)
    if index is not None:
        days = set(d for d in days if days_index[d.day] == index)
    if index_in is not None:
        days = set(d for d in days if days_index[d.day] in index_in)
    if day is not None:
        days = set(d for d in days if d.day == day)
    if day_in is not None:
        days = set(d for d in days if d.day in day_in)
    return days


def corresponding_slot(scheduled_course):
    day = Day(week=scheduled_course.course.week, day=scheduled_course.day)
    start_time = scheduled_course.start_time
    duration = scheduled_course.duration
    department = scheduled_course.course.type.department
    return CourseSlot(day, start_time, duration, department)
