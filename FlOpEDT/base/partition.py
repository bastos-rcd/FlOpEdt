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

from TTapp.TTConstraints.no_course_constraints import NoTutorCourseOnDay
from base.models import CourseStartTimeConstraint, ModulePossibleTutors, ScheduledCourse, TimeGeneralSettings, UserPreference
from base.timing import TimeInterval, Day, days_index, flopdate_to_datetime, time_to_floptime
from datetime import datetime, timedelta
from django.db.models import Q
import copy

class Partition(object):
    '''Partition class to analyse data related by time'''
    def __init__(self, type, date_start, date_end, day_start_time = None, day_end_time = None):
        '''Partition's constructor
        
        Parameters:
            type (str): the type of data the Partition is going to hold
            date_start (datetime): the beginning of its time interval
            date_end (datetime): the end of its time interval
            day_start_time (int) [Optionnal]: the starting time in minutes of the schedule time each day
            day_end_time (int) [Optionnal]: the ending time in minutes of the schedule time each day
            
        If one of the optionnal parameters is missing no day time will be set.'''
        self.intervals = []
        self.type = type
        self.weekend =[]
        self.day_start_time = day_start_time
        self.day_end_time = day_end_time
        self.intervals.append(
            (TimeInterval(date_start, date_end),
                {"available" : False, "forbidden" : False}))
        if day_start_time and day_end_time:
            self.add_night_time(day_start_time, day_end_time)

    @property
    def nb_intervals(self):
        '''The number of intervals of time the partition contains'''
        return len(self.intervals)

    @property
    def duration(self):
        '''The amount of minutes between the begining of the partition and the end'''
        return abs(self.intervals[len(self.intervals)-1][0].end - self.intervals[0][0].start).total_seconds()//60

    @property
    def available_duration(self):
        '''The number of minutes available (and not forbidden) in the partition'''
        avail_duration = 0
        for interval in self.intervals:
            if interval[1]["available"] and not interval[1]["forbidden"]:
                avail_duration += interval[0].duration
        return avail_duration

    @property
    def not_forbidden_duration(self):
        '''The number of minutes not forbidden (available or not) in the partition'''
        not_forbid = 0
        for interval in self.intervals:
            if not interval[1]["forbidden"]:
                not_forbid += interval[0].duration
        return not_forbid
    
    @property
    def day_duration(self):
        '''The number of minutes of day time each day
        Returns:
            (int): 0 if day time is not set'''
        if self.day_start_time and self.day_end_time:
            return (self.day_end_time - self.day_start_time)
        return 0
    
    def get_weekend(self):
        return self.weekend

    def __str__(self):
        return_string = f"Partition starts at {self.intervals[0][0].start} and ends at {self.intervals[self.nb_intervals-1][0].end}\n"
        return_string += f"It contains {self.available_duration} available minutes.\n"
        return_string += f"The intervals are :\n"
        for interval in self.intervals:
            return_string += f"{interval[0]}, {interval[1]}\n"
        return_string += "end."
        return return_string


    def add_lunch_break(self, start_time, end_time):
        '''Add forbidden lunch time to each day of the partition
        
        Parameters:
            start_time (int): the starting time in minutes from midnight of the lunch_break
            end_time (int): the ending time in minutes from midnight of the lunch_break'''
        day = self.intervals[0][0].start
        end_hours = end_time//60
        end_minutes = end_time%60
        start_hours = start_time//60
        start_minutes = start_time%60

        while day < self.intervals[len(self.intervals)-1][0].end:
            self.add_slot(
                TimeInterval(
                    datetime(day.year, day.month, day.day, start_hours, start_minutes, 0),
                    datetime(day.year, day.month, day.day, end_hours, end_minutes, 0)
                ), "lunch_break",
                {"forbidden" : True, "lunch_break": True})
            day = day + timedelta(days = 1)
        if self.intervals[0][0].start > self.intervals[len(self.intervals)-1][0].end:
            self.add_slot(
                TimeInterval(
                    datetime(day.year, day.month, day.day, start_hours, start_minutes, 0),
                    datetime(day.year, day.month, day.day, end_hours, end_minutes, 0)
                ), "lunch_break",
                {"forbidden" : True, "lunch_break": True})
        return True

    def add_week_end(self, days_of_week):
        '''Changes several days to forbidden
        
        Parameters:
            days_of_week (list(str)): a list of days that are not week_end days
            
        days_of_week must have all days in it consecutives'''
        weekend_days = [day for day in [Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY, Day.FRIDAY, Day.SATURDAY, Day.SUNDAY] if not (day in days_of_week)]
        weekend_indexes =  [days_index[day] for day in weekend_days]
        for d in weekend_days :
            self.weekend.append(d)
        i=0
        while weekend_indexes[len(weekend_indexes)-1] - weekend_indexes[0] >= len(weekend_indexes) and i < len(weekend_indexes):
            weekend_indexes.append(weekend_indexes[0]+7)
            weekend_indexes.remove(weekend_indexes[0])
            i+=1
        if weekend_indexes[len(weekend_indexes)-1] - weekend_indexes[0] >= len(weekend_indexes):
            return False
        
        day = self.intervals[0][0].start
        number_of_day_week_end = weekend_indexes[len(weekend_indexes)-1]-weekend_indexes[0]
        #Manque le dernier jour si self.intervals[0][0].start > self.intervals[len(self.intervals)-1][0].end
        while day < self.intervals[len(self.intervals)-1][0].end:
            if day.weekday() == weekend_indexes[0]:
                self.add_slot(
                    TimeInterval(
                        datetime(day.year, day.month, day.day, 0, 0, 0),
                        datetime((day + timedelta(days = number_of_day_week_end+1)).year, (day + timedelta(days = number_of_day_week_end+1)).month, (day + timedelta(days = number_of_day_week_end+1)).day, 0, 0, 0)
                    ), "week_end",
                    {"forbidden" : True, "week_end": True})
                day = day + timedelta(days = number_of_day_week_end)
            else:
                day = day + timedelta(days = 1)
        return True


    def add_night_time(self, day_start_time=None ,day_end_time=None):
        """Changes time intervals to forbidden each days
        
        Parameters:
            day_start_time (int) [Optionnal]: the starting time of the day in minutes since midnight
            day_end_time (int) [Optionnal]: the ending time of the day in minutes since midnight
            
        If the parameters are set they are changing the value of the start and/or end time of the partition"""

        if day_start_time:
            self.day_start_time = day_start_time
        else:
            day_start_time = self.day_start_time

        if day_end_time:
            self.day_end_time = day_end_time
        else:
            day_end_time = self.day_end_time

        day = self.intervals[0][0].start
        end_hours = day_end_time//60
        end_minutes = day_end_time%60
        start_hours = day_start_time//60
        start_minutes = day_start_time%60
        if self.intervals[0][0].start.hour < start_hours or (self.intervals[0][0].start.hour == start_hours
                                                            and self.intervals[0][0].start.minute < start_minutes):
            self.add_slot(TimeInterval(
                datetime(day.year, day.month, day.day, 0, 0, 0),
                datetime(day.year, day.month, day.day, start_hours, start_minutes)
                ), "night_time", {"forbidden" : True, "night_time" : True})
        while day < self.intervals[len(self.intervals)-1][0].end:
            self.add_slot(
                TimeInterval(
                    datetime(day.year, day.month, day.day, end_hours, end_minutes, 0),
                    datetime((day + timedelta(days = 1)).year, (day + timedelta(days = 1)).month, (day + timedelta(days = 1)).day, start_hours, start_minutes, 0)
                ), "night_time",
                {"forbidden" : True, "night_time": True})
            day = day + timedelta(days = 1)



    def nb_slots_available_of_duration(self, duration):
        """Calculates the number of available time in the partition of minimum consecutive duration
        
        Parameters:
            duration (int): the minimum duration of one slot of time
            
        Returns:
            (int): the number of times it founds an available time of minimum duration"""

        current_duration = 0
        nb_slots = 0
        for interval in self.intervals:
            if interval[1]["available"] and not interval[1]["forbidden"]:
                current_duration += interval[0].duration
            else:
                nb_slots += current_duration//duration
                current_duration = 0
        nb_slots += current_duration//duration
        current_duration = 0
        return int(nb_slots)

    def nb_slots_available_of_duration_beginning_at(self, duration, start_times):
        """Calculates the number of available time in the partition of minimum consecutive duration and with specific starting times
        
        Parameters:
            duration (int): the minimum duration of one slot of time
            start_times (list(int)): the list of times in minutes from midnight when the slots can start
            
        Returns:
            (int): the number of times it founds an available time of minimum duration starting at a starting time"""
            
        # on considère ici qu'il existe forcément une nuit, c'est à dire un intervalle à not available qui nous fait passer d'une journée à l'autre
        
        start_times.sort()
        slot_duration = 0
        nb_slots = 0
            
        for interval in self.intervals:
            
            # for each start time we look for a slot
                
            if interval[1]["available"] and not interval[1]["forbidden"]:
                start = time_to_floptime(interval[0].start.time())
                end = time_to_floptime(interval[0].end.time())
                
                # we need to know times already used for a slot in an interval
                
                time_already_use = 0
                
                if slot_duration == 0:
                    for st in start_times:
                        
                        # we look if the current start time is not in a slot already computed
                        
                        if start + st > time_already_use :
                            if start <= st and end > st:
                                slot_duration = interval[0].duration - (st - start)
                                time_already_use += duration
                                if slot_duration >= duration :
                                    nb_slots += 1
                                    slot_duration = 0
                                
                                # slot_duration < duration implies no more time useful in the interval
                                # we keep it to look if there is enough time in the next interval.
                                
                                else :
                                    break
                else:
                    time_already_use += duration - slot_duration
                    slot_duration += interval[0].duration
                    if slot_duration >= duration :
                        nb_slots += 1
                    for st in start_times:
                        if end - st > time_already_use :
                            if start <= st and end > st:
                                slot_duration = interval[0].duration - (st - start)
                                time_already_use += duration
                                if slot_duration >= duration :
                                    nb_slots += 1
                                    slot_duration = 0
                                else :
                                    break
            else:
                slot_duration = 0
    
        return int(nb_slots)



    def nb_slots_not_forbidden_of_duration(self, duration):
        """Calculates the number of time not forbidden in the partition of minimum consecutive duration
        
        Parameters:
            duration (int): the minimum duration of one slot of time
            
        Returns:
            (int): the number of times it founds a non forbidden slot time of minimum duration"""
        current_duration = 0
        nb_slots = 0
        for interval in self.intervals:
            if not interval[1]["forbidden"]:
                current_duration += interval[0].duration
            else:
                nb_slots += current_duration//duration
                current_duration = 0
        nb_slots += current_duration//duration
        current_duration = 0
        return int(nb_slots)

    def nb_slots_not_forbidden_of_duration_beginning_at(self, duration, start_times):
        
        
        """Calculates the number of time not forbidden in the partition of minimum consecutive duration and with specific starting times
        
        Parameters:
            duration (int): the minimum duration of one slot of time
            start_times (list(int)): the list of times in minutes from midnight when the slots can start
            
        Returns:
            (int): the number of times it founds a non forbidden slot time of minimum duration starting at a starting time"""
            
        start_times.sort()
        slot_duration = 0
        nb_slots = 0
            
        for interval in self.intervals:
            
            # for each start time we look for a slot
                
            if not interval[1]["forbidden"]:
                start = time_to_floptime(interval[0].start.time())
                end = time_to_floptime(interval[0].end.time())
                
                # we need to know times already used for a slot in an interval
                
                time_already_use = 0
                
                if slot_duration == 0:
                    for st in start_times:
                        
                        # we look if the current start time is not in a slot already computed
                        
                        if start + st > time_already_use :
                            if start <= st and end > st:
                                slot_duration = interval[0].duration - (st - start)
                                time_already_use += duration
                                if slot_duration >= duration :
                                    nb_slots += 1
                                    slot_duration = 0
                                
                                # slot_duration < duration implies no more time useful in the interval
                                # we keep it to look if there is enough time in the next interval.
                                
                                else :
                                    break
                else:
                    time_already_use += duration - slot_duration
                    slot_duration += interval[0].duration
                    if slot_duration >= duration :
                        nb_slots += 1
                    for st in start_times:
                        if end - st > time_already_use :
                            if start <= st and end > st:
                                slot_duration = interval[0].duration - (st - start)
                                time_already_use += duration
                                if slot_duration >= duration :
                                    nb_slots += 1
                                    slot_duration = 0
                                else :
                                    break
            else:
                slot_duration = 0
    
        return int(nb_slots)
    
    def clear_merge(self):
        '''Checks if several consecutive interval have the same data and if so merge them'''
        length = len(self.intervals)-1
        i = 0
        while i < length:
            if self.intervals[i][1] == self.intervals[i+1][1]:
                self.intervals[i][0].end = self.intervals[i+1][0].end
                self.intervals.remove(self.intervals[i+1])
                length-=1
            else:
                i+=1

    def add_partition(self, other):
        """Add all intervals from the other partition to the self one"""
        if isinstance(other, Partition):
            for interval in other.intervals:
                self.add_slot(interval[0], "all", interval[1])

    def add_partition_data_type(self, other, key):
        """Add all intervals with key in the data from the other partition to the self one"""
        if isinstance(other, Partition):
            for interval in other.intervals:
                if key in interval[1]:
                    self.add_slot(interval[0], "all", interval[1])

    def find_first_timeinterval_with_key(self, key, duration = None):
        """Find the first time interval in the partition with a specific key in its data
        
        Parameters:
            key (any): the key searched in the data dictionary of the interval
            duration (int) [Optionnal]: the minimum duration of the time interval we want to find
            
        Returns:
            (TimeInterval): the time interval found"""
        start = None
        i = 0
        intervalle = None
        while i < len(self.intervals) and intervalle == None:
            if key in self.intervals[i][1]:
                start = self.intervals[i][0].start
                while i < len(self.intervals) and key in self.intervals[i][1]:
                    i+=1
                if start + timedelta(hours = duration//60, minutes=duration%60) <= self.intervals[i][0].start: 
                    intervalle = TimeInterval(start, self.intervals[i][0].start)
            i+=1
        return intervalle

    def find_all_available_timeinterval_with_key(self, key, duration = None):
        """Find all time intervals in the partition with a specific key in their data
        
        Parameters:
            key (any): the key searched in the data dictionary of the intervals
            duration (int) [Optionnal]: the minimum duration of the time intervals we want to find
            
        Returns:
            (list(TimeInterval)): the time intervals found"""
        start = None
        i = 0
        result = []
        while i < len(self.intervals):
            if key in self.intervals[i][1] and self.intervals[i][1]["available"] and not self.intervals[i][1]["forbidden"]:
                current_duration = 0
                start = self.intervals[i][0].start
                while i < len(self.intervals) and key in self.intervals[i][1] and self.intervals[i][1]["available"] and not self.intervals[i][1]["forbidden"]:
                    current_duration+=self.intervals[i][0].duration
                    i+=1
                if (duration == None or current_duration > duration):
                    result.append(TimeInterval(start, self.intervals[i-1][0].end))
            i+=1
        return result

    def find_all_available_timeinterval_with_key_starting_at(self, key, start_times, duration = None):
        """Find all time intervals in the partition with a specific key in their data and with specific starting times
        
        Parameters:
            key (any): the key searched in the data dictionary of the intervals
            duration (int) [Optionnal]: the minimum duration of the time intervals we want to find
            start_times (list(int)): the list of times in minutes from midnight when the slots can start
            
        Returns:
            (list(TimeInterval)): the time intervals found"""
        start = None
        i = 0
        result = []
        while i < len(self.intervals):
            if key in self.intervals[i][1] and self.intervals[i][1]["available"] and not self.intervals[i][1]["forbidden"]:
                for st in start_times:
                    if time_to_floptime(self.intervals[i][0].start.time()) <= st and time_to_floptime(self.intervals[i][0].end.time()) > st:
                        dif = st - time_to_floptime(self.intervals[i][0].start.time())
                        datetime_start = self.intervals[i][0].start + timedelta(hours = dif/60)
                        start = st
                        break
                else:
                    i+=1
                    continue
                current_duration = self.intervals[i][0].duration - (start - time_to_floptime(self.intervals[i][0].start.time()))
                i+=1
                while i < len(self.intervals) and key in self.intervals[i][1] and self.intervals[i][1]["available"] and not self.intervals[i][1]["forbidden"]:
                    current_duration+=self.intervals[i][0].duration
                    i+=1
                if (duration == None or current_duration >= duration):
                    result.append(TimeInterval(datetime_start, self.intervals[i-1][0].end))
                start = None
            i+=1
        return result


    def add_slot(self, interval, data_type, data):
        """Add an interval of time with data related to it to the Partition.
        Linear complexity on the size of self.
        
        Parameters:
            interval (TimeInterval) : The interval of time we are going to add
            data_type (str) : The type of data we are going to add
            data (dict) : The data we are going to add
            
        Returns:
            boolean: True if the interval was in the Partition time or False otherwise
            
            
        Data type can be:
            - "user_preference" : with keys "tutor" and "available"
            - "night_time" : with keys "night_time" and "forbidden"
            - "lunch_break" : with keys "lunch_break" and "forbidden"
            - "week_end" : with keys "week_end" and "forbidden" 
            - "no_course_tutor" : with keys "no_course_tutor"
            - "scheduled_course" : with key "forbidden"
            - "holiday" : with key "forbidden"
            - "all" : with any key in it """
        i = 0
        #Check if we are in the interval range
        if (interval.start >= self.intervals[len(self.intervals)-1][0].end
                or interval.end <= self.intervals[0][0].start):
            return False

        while self.intervals[i][0].end <= interval.start:
            i += 1
        
        while i < len(self.intervals) and interval.end > self.intervals[i][0].start:
            if(interval.start == self.intervals[i][0].end):
                i+=1
            if i == 0 and self.intervals[i][0].start > interval.start:
                interval.start = self.intervals[i][0].start
            if i == len(self.intervals)-1 and self.intervals[i][0].end < interval.end:
                interval.end = self.intervals[i][0].end
            #IF WE ALREADY HAVE THE SAME INTERVAL WE APPEND THE DATA
            if self.intervals[i][0] == interval:
                self.add_data(data_type, copy.deepcopy(data), i)
                i += 1
            #IF WE ARE INSIDE AN EXISTING INTERVAL
            elif self.intervals[i][0].start <= interval.start and self.intervals[i][0].end >= interval.end:
                new_part = 1
                if self.intervals[i][0].end != interval.end:
                    self.intervals.insert(i+1, (TimeInterval(interval.end, self.intervals[i][0].end),
                                                            copy.deepcopy(self.intervals[i][1])))
                    self.intervals[i][0].end = interval.end
                if self.intervals[i][0].start != interval.start:
                    self.intervals[i][0].end = interval.start
                    self.intervals.insert(i+1, (TimeInterval(interval.start, interval.end), copy.deepcopy(self.intervals[i][1])))
                    self.add_data(data_type, copy.deepcopy(data), i+1)
                    new_part += 1
                else:
                    self.add_data(data_type, copy.deepcopy(data), i)
                i += new_part
            #ELSE WE ARE IN BETWEEN TWO OR MORE INTERVALS
            else:
                #The TimeInterval at the index i is inside our new TimeInterval
                if self.intervals[i][0].start == interval.start:
                    self.add_data(data_type, copy.deepcopy(data), i)
                    interval.start = self.intervals[i+1][0].start
                #Our new TimeInterval is cut by the ones at the index i and i+1
                elif self.intervals[i][0].end > interval.start:
                    self.intervals[i][0].end = interval.start
                    self.intervals.insert(i+1, (TimeInterval(interval.start, self.intervals[i+1][0].start), copy.deepcopy(self.intervals[i][1])))
                    self.add_data(data_type, copy.deepcopy(data), i+1)
                    i += 2
                    interval.start = self.intervals[i][0].start
        return True

    def add_data(self, data_type, data, interval_index):
        '''Adds some data to an interval
        Linear complexity on the size of the data in the data_type key.

        Parameters:
            data_type (str): the type of date added
            data (dict): a dictionary containing the data
            interval_index (int): the index of self.intervals where we want to put the data in
            
        Returns:
            (None)
        Internal method not to be called by user'''
        if "available" in data:
            self.intervals[interval_index][1]["available"] = self.intervals[interval_index][1]["available"] or data["available"]
        if "forbidden" in data:
            self.intervals[interval_index][1]["forbidden"] = self.intervals[interval_index][1]["forbidden"] or data["forbidden"]
        if not data_type in self.intervals[interval_index][1] and data_type != "all" and data_type != 'scheduled_course':
            self.intervals[interval_index][1][data_type] = dict()
        if data_type == "user_preference":
            self.intervals[interval_index][1][data_type][data["tutor"]] = data["value"]
        elif data_type == "night_time" or data_type == "lunch_break" or data_type == "week_end":
            self.intervals[interval_index][1][data_type] = data[data_type]
        elif data_type == "no_course_tutor":
            if "period" in self.intervals[interval_index][1][data_type]:
                for p in data[data_type]["period"]:
                    self.intervals[interval_index][1][data_type]["period"].add(p)
            else:
                self.intervals[interval_index][1][data_type]["period"] = data[data_type]["period"]
            if "tutors" in self.intervals[interval_index][1][data_type]:
                for t in data[data_type]["tutors"]:
                    self.intervals[interval_index][1][data_type]["tutors"].add(t)
            else:
                self.intervals[interval_index][1][data_type]["tutors"] = data[data_type]["tutors"]

            if "tutor_status" in self.intervals[interval_index][1][data_type]:
                for ts in data[data_type]["tutor_status"]:
                    self.intervals[interval_index][1][data_type]["tutor_status"].add(ts)
            else:
                self.intervals[interval_index][1][data_type]["tutor_status"] = data[data_type]["tutor_status"]
        elif data_type == 'scheduled_course':
            if not data_type in self.intervals[interval_index][1]:
                self.intervals[interval_index][1][data_type] = [data[data_type]]
            self.intervals[interval_index][1][data_type].append(data[data_type])
        elif data_type == "all":
            for key, value in data.items():
                if key != "available" and key != "forbidden":
                    self.intervals[interval_index][1][key] = value

    @staticmethod
    def get_partition_of_week(week, department, with_day_time = False):
        """Considering a week and a department we built and return a partition with minimum data in it
        Complexity on O(1)

        Parameters:
            week (Week): the week we want to consider to build the partition
            department (Department): the department we're gonna get the TimeGeneralSettings data from
            with_day_time (boolean): determine if the partition will contain lunch breaks and night times
                        
        Returns:
            (None)"""
        time_settings = TimeGeneralSettings.objects.get(department = department)
        day_start_week = Day(time_settings.days[0], week)
        day_end_week = Day(time_settings.days[len(time_settings.days)-1], week)
        start_week = flopdate_to_datetime(day_start_week, time_settings.day_start_time)
        end_week = flopdate_to_datetime(day_end_week, time_settings.day_finish_time)
        considered_week_partition = Partition("None", start_week, end_week)
        if with_day_time:
            considered_week_partition.add_lunch_break(time_settings.lunch_break_start_time, time_settings.lunch_break_finish_time)
            considered_week_partition.add_night_time(time_settings.day_start_time, time_settings.day_finish_time)
        return considered_week_partition

    def add_scheduled_courses_to_partition(self, week, department, tutor = None, forbidden = False):
        """Add all scheduled courses of other department to the partition.
        Complexity on O(s*i) s being the number of scheduled courses and i being the number of interval inside the partition.
        
        Parameters:
            week (Week): the week we want to consider to get the scheduled courses from
            department (Department): the department from which we don't want any courses
            tutor (Tutor) [Optionnal]: the tutor teaching the scheduled courses, if None takes all scheduled courses
            forbidden (boolean) [Optionnal]: whether we want to consider all intervals as being forbidden or not
            
        Returns:
            (None)"""
        other_departments_sched_courses = self.get_other_department_scheduled_courses(week, department, tutor)
        for sc_course in other_departments_sched_courses:
            data = {"scheduled_course" : sc_course}
            if forbidden:
                data["forbidden"] = True
            self.add_slot(
                TimeInterval(
                    flopdate_to_datetime(Day(sc_course.day, week), sc_course.start_time),
                    flopdate_to_datetime(Day(sc_course.day, week), sc_course.end_time)
                ),
                "scheduled_course",
                data
            )

    @staticmethod
    def get_other_department_scheduled_courses(week, department, tutor = None, room = None):
        """Retrieve all scheduled courses for the other departments
        Complexity on O(1)
        
        Parameters:
            week (Week): the week we want to consider to get the scheduled courses from
            department (Department): the department from which we don't want any courses
            tutor (Tutor) [Optionnal]: the tutor teaching the scheduled courses, if None takes all scheduled courses
            
        Returns:
            (Queryset(ScheduledCourses)): The scheduled courses we want as a queryset"""
        if tutor:
            return (ScheduledCourse.objects
                        .filter(Q(tutor = tutor) | Q(course__supp_tutor = tutor), course__week = week ,work_copy=0)
                        .exclude(course__type__department=department))
        else:
            return (ScheduledCourse.objects
                        .filter(course__week = week ,work_copy=0)
                        .exclude(course__type__department=department))

    @staticmethod
    def get_available_partition_for_course(course, week, department):
        """ Build and returns a partition with all available intervals and data for a specific course.
        Complexity on O(i) with i being the size of the partition.
        
        Parameters:
            course (Course): the course we want to retrieve data for
            week (Week): the week we want to consider
            department (Department): the department we're gonna get the TimeGeneralSettings data from
        
        Returns:
            (Partition): None if there is no tutor's availability for the course and the correct partition otherwise
        
        """
        week_partition = Partition.get_partition_of_week(week, department, True)
        possible_tutors_1 = set()
        required_supp_1 = set()
        if course.tutor is not None:
            possible_tutors_1.add(course.tutor)
        elif ModulePossibleTutors.objects.filter(module = course.module).exists():
            possible_tutors_1 = set(ModulePossibleTutors.objects.get(module = course.module).possible_tutors.all())
        else:
            mods_possible_tutor = ModulePossibleTutors.objects.filter(module__train_prog__department = department)
            possible_tutors_1 = set(mod.possible_tutors.all() for mod in mods_possible_tutor)

        if course.supp_tutor is not None:
            required_supp_1 = set(course.supp_tutor.all())

        D1 = UserPreference.objects.filter(user__in=possible_tutors_1, week=week, value__gte=1)
        if not D1:
            D1 = UserPreference.objects.filter(user__in=possible_tutors_1, week=None, value__gte=1)
        if D1:
            # Retrieving constraints for days were tutors shouldn't be working
            no_course_tutor1 = (NoTutorCourseOnDay.objects
                .filter(Q(tutors__in = required_supp_1.union(possible_tutors_1))
                    | Q(tutor_status = [pt.status for pt in required_supp_1.union(possible_tutors_1)]),
                    weeks = week))
            if not no_course_tutor1:
                no_course_tutor1 = (NoTutorCourseOnDay.objects
                .filter(Q(tutors__in = required_supp_1.union(possible_tutors_1))
                    | Q(tutor_status = [pt.status for pt in required_supp_1.union(possible_tutors_1)]),
                    weeks = None))

            # Adding all user preferences to the partition
            for up in D1:
                up_day = Day(up.day, week)
                week_partition.add_slot(
                    TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                    flopdate_to_datetime(up_day, up.end_time)),
                    "user_preference",
                    {"value" : up.value, "available" : True, "tutor" : up.user}
                )

            # Retrieving no tutor course constraint slots and adding them to the partition
            # Slots are not set to be forbidden
            for constraint in no_course_tutor1:
                slot = constraint.get_slot_constraint(week)
                if slot:
                    week_partition.add_slot(
                        slot[0],
                        "no_course_tutor",
                        slot[1]
                    )

            for interval in week_partition.intervals:
                    if not NoTutorCourseOnDay.tutor_and_supp(interval, required_supp_1, possible_tutors_1):
                        interval[1]["available"] = False
            
            if required_supp_1:
                #Retrieving and adding user preferences for the required tutors
                RUS1 = UserPreference.objects.filter(user__in=required_supp_1, week=week, value__gte=1)
                if not RUS1:
                    RUS1 = UserPreference.objects.filter(user__in=required_supp_1, week=None, value__gte=1)

                for up in RUS1:
                    up_day = Day(up.day, week)
                    week_partition.add_slot(
                        TimeInterval(flopdate_to_datetime(up_day, up.start_time),
                        flopdate_to_datetime(up_day, up.end_time)),
                        "user_preference",
                        {"value" : up.value, "available" : True, "tutor" : up.user}
                    )

                for interval in week_partition.intervals:
                    if not NoTutorCourseOnDay.tutor_and_supp(interval, required_supp_1, possible_tutors_1):
                        interval[1]["available"] = False
            return week_partition   
        return None
