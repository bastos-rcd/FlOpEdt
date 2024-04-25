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
# you develop activities involving the F*lOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

from rest_framework import serializers
from base.timing import floptime_to_time
from base.models import ScheduledCourse, Module, GenericGroup, Room
from people.models import Tutor


def sched_course_else_null(func):
    def wrapper(self, obj):
        if not isinstance(obj, ScheduledCourse):
            return ""
        return func(self, obj)

    return wrapper


class CelcatExportSerializer(serializers.Serializer):
    _event_id = serializers.SerializerMethodField()
    _day_of_week = serializers.SerializerMethodField()
    _start_time = serializers.SerializerMethodField()
    _end_time = serializers.SerializerMethodField()
    _weeks = serializers.SerializerMethodField()
    _event_name = serializers.SerializerMethodField()
    _break_mins = serializers.SerializerMethodField()
    _spanName = serializers.SerializerMethodField()
    _event_catName = serializers.SerializerMethodField()
    _custom1 = serializers.SerializerMethodField()
    _custom2 = serializers.SerializerMethodField()
    _custom3 = serializers.SerializerMethodField()
    _capacity_req = serializers.SerializerMethodField()
    _deptName = serializers.SerializerMethodField()
    _global_event = serializers.SerializerMethodField()
    _protected = serializers.SerializerMethodField()
    _suspended = serializers.SerializerMethodField()
    _grouping_id = serializers.SerializerMethodField()
    _registers_req = serializers.SerializerMethodField()
    _lock = serializers.SerializerMethodField()
    _notes = serializers.SerializerMethodField()
    _resType = serializers.SerializerMethodField()
    _resName = serializers.SerializerMethodField()
    _resWeeks = serializers.SerializerMethodField()
    _layoutName = serializers.SerializerMethodField()
    _staff_catName = serializers.SerializerMethodField()
    _quantity = serializers.SerializerMethodField()

    def get__event_id(self, obj):
        return ""

    @sched_course_else_null
    def get__day_of_week(self, obj):
        local_day_dict = {
            "m": "Mon",
            "tu": "Tue",
            "w": "Wed",
            "th": "Thu",
            "f": "Fri",
            "sa": "Sat",
            "su": "Sun",
        }
        return local_day_dict[obj.day]

    @sched_course_else_null
    def get__start_time(self, obj):
        return floptime_to_time(obj.start_time).strftime("%H:%M")

    @sched_course_else_null
    def get__end_time(self, obj):
        return floptime_to_time(obj.end_time).strftime("%H:%M")

    @sched_course_else_null
    def get__weeks(self, obj):
        real_week_nb = obj.course.week.nb
        if real_week_nb < 34:
            return real_week_nb + 18
        else:
            return real_week_nb - 33

    def get__event_name(self, obj):
        return ""

    @sched_course_else_null
    def get__break_mins(self, obj):
        return 0

    def get__spanName(self, obj):
        return ""

    @sched_course_else_null
    def get__event_catName(self, obj):
        return obj.course.type.name

    def get__custom1(self, obj):
        return ""

    def get__custom2(self, obj):
        return ""

    def get__custom3(self, obj):
        return ""

    def get__capacity_req(self, obj):
        return ""

    @sched_course_else_null
    def get__deptName(self, obj):
        return obj.course.type.department.abbrev

    @sched_course_else_null
    def get__global_event(self, obj):
        return "N"

    @sched_course_else_null
    def get__protected(self, obj):
        return "N"

    @sched_course_else_null
    def get__suspended(self, obj):
        return "N"

    def get__grouping_id(self, obj):
        return ""

    def get__registers_req(self, obj):
        return ""

    def get__lock(self, obj):
        return ""

    @sched_course_else_null
    def get__notes(self, obj):
        if hasattr(obj, "additional"):
            return obj.additional.comment
        return ""

    def get__resType(self, obj):
        if isinstance(obj, ScheduledCourse):
            return ""
        elif isinstance(obj, Module):
            return "Module"
        elif isinstance(obj, GenericGroup):
            return "Group"
        elif isinstance(obj, Room):
            return "Room"
        else:
            return "Staff"

    def get__resName(self, obj):
        if obj is None:
            return ""
        elif isinstance(obj, ScheduledCourse):
            return ""
        elif isinstance(obj, Module):
            return obj.abbrev
        elif isinstance(obj, GenericGroup):
            return obj.name
        elif isinstance(obj, Tutor):
            return obj.username
        elif isinstance(obj, Room):
            return obj.name
        else:
            return ""

    def get__resWeeks(self, obj):
        return ""

    def get__layoutName(self, obj):
        return ""

    def get__staff_catName(self, obj):
        return ""

    def get__quantity(self, obj):
        return ""
