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

from rest_framework import serializers

from base.models import CourseType


class VolumeAgrege:
    conditions_for_continuous = []
    continuous_factor = {}

    def __init__(self, agg_dict):
        self.module_id = agg_dict["module_id"]
        self.tutor_id = agg_dict["tutor__id"]
        self.course_type_id = agg_dict["course_type_id"]
        self.module_ppn = agg_dict["module_ppn"]
        self.module_name = agg_dict["module_name"]
        self.tutor_username = agg_dict["tutor_username"]
        self.tutor_first_name = agg_dict["tutor_first_name"]
        self.tutor_last_name = agg_dict["tutor_last_name"]
        self.course_type_name = agg_dict["course_type_name"]
        self.duration = agg_dict["duration"]
        self.pay_duration = agg_dict["pay_duration"]
        self.itinial_training = 0
        self.continuous_training = 0
        self.conditional_add(agg_dict, True)

    def conditional_add(self, agg_dict, ok):
        if ok:
            course_type_id = agg_dict["type_id"]
            course_type = CourseType.objects.get(id=course_type_id)
            dept_abbrev = course_type.department.abbrev
            duration = agg_dict["pay_duration"]
            if duration is None:
                duration = agg_dict["duration"]
            volume = agg_dict["slots_nb"] * duration
            toadd_continuous = 0
            for cpc in self.conditions_for_continuous:
                if all(agg_dict[key] == cpc[key] for key in cpc):
                    ct_name = course_type.name
                    toadd_continuous = volume
                    if dept_abbrev in self.continuous_factor:
                        if ct_name in self.continuous_factor[dept_abbrev]:
                            toadd_continuous *= self.continuous_factor[dept_abbrev][
                                ct_name
                            ]
            self.continuous_training += toadd_continuous
            self.itinial_training += volume - toadd_continuous
            return None
        else:
            return VolumeAgrege(agg_dict)

    def add(self, agg_dict):
        return self.conditional_add(
            agg_dict,
            self.module_id == agg_dict["module_id"]
            and self.tutor_id == agg_dict["tutor__id"]
            and self.course_type_id == agg_dict["course_type_id"],
        )

    def __str__(self):
        return f"{self.tutor_username} {self.module_ppn} {self.course_type_name} ({self.itinial_training}|{self.continuous_training})"


class ScheduledCoursePaySerializer(serializers.Serializer):
    module_ppn = serializers.CharField()
    module_name = serializers.CharField()
    tutor_username = serializers.CharField()
    tutor_firs_name = serializers.CharField()
    tutor_last_name = serializers.CharField()
    course_type_name = serializers.CharField()
    initial_training = serializers.FloatField()
    continuous_training = serializers.FloatField()


class DailyVolumeSerializer(serializers.Serializer):
    month = serializers.CharField()
    date = serializers.DateField()
    other = serializers.FloatField()
    td = serializers.FloatField()
    tp = serializers.FloatField()


class RoomDailyVolumeSerializer(serializers.Serializer):
    date = serializers.DateField()
    volume = serializers.FloatField()


class DuplicateSerializer(serializers.Serializer):
    date = serializers.DateField()
    time = serializers.CharField()
    type = serializers.CharField()
    tutor = serializers.CharField()
    nb = serializers.IntegerField()
