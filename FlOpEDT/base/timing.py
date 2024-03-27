"""
 This file is part of the FlOpEDT/FlOpScheduler project.
 Copyright (c) 2017
 Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public
 License along with this program. If not, see
 <http://www.gnu.org/licenses/>.

 You can be released from the requirements of the license by purchasing
 a commercial license. Buying such a license is mandatory as soon as
 you develop activities involving the FlOpEDT/FlOpScheduler software
 without disclosing the source code of your own applications.

 helpers for time management
 ---------------------------
"""

import datetime as dt

from django.utils.translation import gettext_lazy as _

import base.models as bm

slot_pause = dt.timedelta(minutes=30)


class Day:
    MONDAY = "m"
    TUESDAY = "tu"
    WEDNESDAY = "w"
    THURSDAY = "th"
    FRIDAY = "f"
    SATURDAY = "sa"
    SUNDAY = "su"

    CHOICES = (
        (MONDAY, _("monday")),
        (TUESDAY, _("tuesday")),
        (WEDNESDAY, _("wednesday")),
        (THURSDAY, _("thursday")),
        (FRIDAY, _("friday")),
        (SATURDAY, _("saturday")),
        (SUNDAY, _("sunday")),
    )

    def __init__(self, day, week):
        self.day = day
        self.week = week

    def __str__(self):
        # return self.nom[:3]
        return self.day + "_s" + str(self.week)

    def __repr__(self):
        return self.day + "_s" + str(self.week)

    def equals(self, other):
        if isinstance(other, Day):
            return self.week == other.week and self.day == other.day
        return False

    def __lt__(self, other):
        if isinstance(other, Day):
            return days_index[self.day] < days_index[other.day]
        return False

    def __gt__(self, other):
        if isinstance(other, Day):
            return days_index[self.day] > days_index[other.day]
        return False

    def __le__(self, other):
        return self.equals(other) or self < other

    def __ge__(self, other):
        return self.equals(other) or self > other


days_list = [c[0] for c in Day.CHOICES]
days_index = {}
for c in Day.CHOICES:
    days_index[c[0]] = days_list.index(c[0])


def hr_min(t):
    h = t // 60
    m = t - h * 60
    return h, m


def min_to_str(t, sep=":"):
    """Convert minute number into input time format

    :param minutes: integer minutes
    :return: string in hour:minute format

    """
    h, m = hr_min(t)
    return f"{h:02d}{sep}{m:02d}"


def str_slot(day, start_time, duration):
    return f"{day}. {start_time}" + f"-{start_time + duration}"


def french_format(minutes):
    """Convert minute number into french time format

    :param minutes: integer minutes
    :return: string in hour h minute format

    """
    return min_to_str(minutes, sep="h")


def str_to_min(time_string, sep=":"):
    """Convert input time format into minute number

    :param time_string string in hour:minute format
    :return: Integer minutes

    """
    hours_minutes = time_string.split(sep)
    return int(hours_minutes[0]) * 60 + int(hours_minutes[1])


def str_to_time(time_string, sep=":"):
    """Convert input time format into time object

    :param time_string string in hour:minute format
    :return: datetime.time object

    """
    hour, minute = time_string.split(sep)
    return dt.time(hour, minute)


def time_to_str(t, sep=":"):
    """Convert datetime.time object into input time format

    :param minutes: datetime.time object
    :return: string in hour:minute format

    """
    h, m = t.hour, t.minute
    return f"{h:02d}{sep}{m:02d}"


################################################################
###TRANSLATION FUNCTIONS BETWEEN FLOPDATES AND PYTHON'S DATES###


# Returns the index of the first monday of the given year.
# Argument "day" being a flop_day type
def first_day_first_week(day):
    year = day.week.year
    if year == 0:
        year = 1
    i = 1
    first = dt.datetime(year, 1, i)
    while first.weekday() != 0:
        i += 1
        first = dt.datetime(year, 1, i)
    return i - 1


##Takes a day (with week and year)
# and returns the date object corresponding
def flopday_to_date(day):
    us_day_index = (days_index[day.day] + 1) % 7
    if day.week is None:
        day_string = f"0001-1-{us_day_index}"
    else:
        four_digit_year = str(day.week.year)
        if len(four_digit_year) < 4:
            four_digit_year = (4 - len(four_digit_year)) * "0" + four_digit_year
        day_string = f"{four_digit_year}-{day.week.nb}-{us_day_index}"
    return dt.datetime.strptime(day_string, "%Y-%W-%w").date()


###TRANSLATION FUNCTIONS BETWEEN FLOPDATES AND PYTHON'S DATES###
################################################################


# will not be used
# TO BE DELETED at the end
class Time:
    AM = "AM"
    PM = "PM"
    HALF_DAY_CHOICES = ((AM, _("AM")), (PM, _("PM")))


class TimeInterval:
    # date_start, date_end : dt.datetime
    def __init__(self, date_start, date_end):
        if date_start > date_end:
            self.start = date_end
            self.end = date_start
        else:
            self.start = date_start
            self.end = date_end

    def __str__(self):
        return f"//intervalle: {self.start} ---> {self.end} //"

    def __repr__(self):
        return f"//intervalle: {self.start} ---> {self.end} //"

    def __eq__(self, other):
        return (
            isinstance(other, TimeInterval)
            and self.start == other.start
            and self.end == other.end
        )

    # An interval is considered less than another one if
    # it ends before or at the same time the other one starts
    def __lt__(self, other):
        return isinstance(other, TimeInterval) and self.end <= other.start

    # An interval is considered greater than another one if
    # it starts after or at the same time the other one ends
    def __gt__(self, other):
        return isinstance(other, TimeInterval) and self.start >= other.end

    # An interval is considered greater or equal to another one if
    # it starts and ends after or at the same moment
    def __ge__(self, other):
        return (
            isinstance(other, TimeInterval)
            and self.start >= other.start
            and self.end >= other.end
        )

    # An interval is considered less or equal to another one if
    # it starts and ends before or at the same moment
    def __le__(self, other):
        return (
            isinstance(other, TimeInterval)
            and self.start <= other.start
            and self.end <= other.end
        )

    @property
    def duration(self):
        # datetime1 - datetime2 = timedelta
        return abs(self.start - self.end)


def all_possible_start_times(department):
    apst_set = set()
    for cstc in department.coursestarttimeconstraint_set.all():
        for start_time in cstc.allowed_start_times:
            apst_set.add(start_time.strftime("%H:%M"))
    apst_list = list(apst_set)
    apst_list.sort()
    return apst_list


def get_default_date(date):
    return dt.date.fromisocalendar(1, 1, date.weekday() + 1)


def add_duration_to_time(time: dt.time, duration: dt.timedelta):
    return (dt.datetime.combine(dt.date.today(), time) + duration).time()


def get_all_scheduling_periods(department):
    if department is None:
        return bm.SchedulingPeriod.objects.all()
    if department.timegeneralsettings.scheduling_period_mode == bm.PeriodEnum.CUSTOM:
        return department.schedulingperiod_set.all()
    return bm.SchedulingPeriod.objects.filter(
        mode=department.timegeneralsettings.scheduling_period_mode
    )
