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
from datetime import date, time, datetime
from enum import Enum

def hr_min(t):
    h = t//60
    m = t - h*60
    return h, m


def hhmm(t):
    h,m = hr_min(t)
    return f'{h:02d}:{m:02d}'


def str_slot(day, start_time, duration):
    return f"{day}. {hhmm(start_time)}" + \
        f"-{hhmm(start_time + duration)}"


def min_to_str(minutes):
    """Convert minute number into input time format

    :param minutes: integer minutes
    :return: string in hour:minute format

    """
    return "%02d:%02d" % hr_min(minutes)


def french_format(minutes):
    """Convert minute number into french time format

    :param minutes: integer minutes
    :return: string in hour h minute format

    """
    result = str(minutes//60) + 'h'
    minutes = minutes % 60
    if 0 < minutes < 10:
        result += '0' + str(minutes)
    elif minutes >= 10:
        result += str(minutes)
    return result


def str_to_min(time_string):
    """Convert input time format into minute number

    :param time_string string in hour:minute format
    :return: Integer minutes

    """
    hours_minutes = time_string.split(':')
    return int(hours_minutes[0]) * 60 + int(hours_minutes[1])


################################################################
###TRANSLATION FUNCTIONS BETWEEN FLOPDATES AND PYTHON'S DATES###

#Returns the index of the first monday of the given year.
#Argument "day" being a flop_day type
def first_day_first_week(day):
    i = 1
    first = datetime(day.week.year, 1, i)
    while first.weekday() != 0:
        i+=1
        first = datetime(day.week.year, 1, i)
    return i - 1


#Takes a day (with week and year) and a starting time
#and returns the datetime object corresponding
def flopdate_to_datetime(day, time):
    day_date = flopday_to_date(day)
    time_day = floptime_to_time(time)
    return datetime.combine(day_date, time_day)


##Takes a day (with week and year)
#and returns the date object corresponding
def flopday_to_date(day):
    nb_leap_year = day.week.year // 4 - day.week.year // 100 + day.week.year // 400
    return date.fromordinal((day.week.year-1) * 365 + (day.week.nb-1)*7 + days_index[day.day] + 1 + nb_leap_year + first_day_first_week(day))


#Takes a starting time
#and returns the time object corresponding
def floptime_to_time(time_minutes):
    return time(time_minutes//60, time_minutes%60)


def time_to_floptime(time_data):
    return time_data.hour*60 + time_data.minute


def date_to_flopday(date):
    isocalendar = date.isocalendar()
    flop_week = Week.objects.get(nb=isocalendar[1], year=isocalendar[0])
    flop_day = Day.CHOICES[isocalendar[2] - 1][0]
    return Day(week=flop_week, day=flop_day)


def datetime_to_floptime(datetime):
    flopday = date_to_flopday(datetime.date())
    floptime = time_to_floptime(datetime.time())
    return flopday, floptime
###TRANSLATION FUNCTIONS BETWEEN FLOPDATES AND PYTHON'S DATES###
################################################################

# will not be used
# TO BE DELETED at the end
class Time:
    AM = 'AM'
    PM = 'PM'
    HALF_DAY_CHOICES = ((AM, 'AM'), (PM, 'PM'))

class TimeInterval(object):

    #date_start, date_end : datetime
    def __init__(self, date_start, date_end):
        if date_start > date_end:
            self.start = date_end
            self.end = date_start
        else:
            self.start = date_start
            self.end = date_end

    def __str__(self):
        return f'//intervalle: {self.start} ---> {self.end} //'

    def __repr__(self):
        return f'//intervalle: {self.start} ---> {self.end} //'

    def __eq__(self, other):
        return isinstance(other, TimeInterval) and self.start == other.start and self.end == other.end

    #An interval is considered less than another one if
    #it ends before or at the same time the other one starts
    def __lt__(self, other):
        return isinstance(other, TimeInterval) and self.end <= other.start

    #An interval is considered greater than another one if
    #it starts after or at the same time the other one ends
    def __gt__(self, other):
        return isinstance(other, TimeInterval) and self.start >= other.end
    
    #An interval is considered greater or equal to another one if
    #it starts and ends after or at the same moment
    def __ge__(self, other):
        return isinstance(other, TimeInterval) and self.start >= other.start and self.end >= other.end

    #An interval is considered less or equal to another one if
    #it starts and ends before or at the same moment
    def __le__(self, other):
        return isinstance(other, TimeInterval) and self.start <= other.start and self.end <= other.end

    @property
    def duration(self):
      #datetime1 - datetime2 = timedelta
      return abs(self.start - self.end).total_seconds()//60
    
    #Build a TimeInterval from a Flop-based day date type
    @staticmethod
    def from_flop_date(day, start_time, duration = None, end_time = None):
        if not duration and not end_time:
            return None
        if not end_time:
            end_time = start_time + duration
        return TimeInterval(flopdate_to_datetime(day, start_time), flopdate_to_datetime(day, end_time))


class Day(object):
  MONDAY = "m"
  TUESDAY = "tu"
  WEDNESDAY = "w"
  THURSDAY = "th"
  FRIDAY = "f"
  SATURDAY = "sa"
  SUNDAY = "su"

  CHOICES = ((MONDAY, "monday"), (TUESDAY, "tuesday"),
              (WEDNESDAY, "wednesday"), (THURSDAY, "thursday"),
              (FRIDAY, "friday"), (SATURDAY, "saturday"),
              (SUNDAY, "sunday"))

  def __init__(self, day, week):
      self.day = day
      self.week = week

  def __str__(self):
      # return self.nom[:3]
      return self.day + '_s' + str(self.week)

  def __repr__(self):
      return self.day + '_s' + str(self.week)

  def __lt__(self, other):
      if isinstance(other, Day):
          return days_index(self.day) < days_index(other.day)
      else:
          return False

  def __gt__(self, other):
      if isinstance(other, Day):
          return days_index(self.day) > days_index(other.day)
      else:
          return False

  def __le__(self, other):
      return self == other or self < other

  def __ge__(self, other):
      return self == other or self > other
    

days_list = [c[0] for c in Day.CHOICES]
days_index = {}
for c in Day.CHOICES:
    days_index[c[0]] = days_list.index(c[0])

def all_possible_start_times(department):
    apst_set = set()
    CT = department.coursetype_set.all()
    for ct in CT:
        for cstc in ct.coursestarttimeconstraint_set.all():
           apst_set |= set(cstc.allowed_start_times)
    apst_list = list(apst_set)
    apst_list.sort()
    return apst_list
