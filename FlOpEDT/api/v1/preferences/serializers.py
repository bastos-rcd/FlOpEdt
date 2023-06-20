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
import base.models as bm
from base.timing import Day, flopdate_to_datetime
from datetime import timedelta

# -----------------
# -- PREFERENCES --
# -----------------
class PreferenceSerializer(serializers.ModelSerializer):
    # TODO V1: change into DatetimeFields
    # start_time = serializers.DatetimeField()
    # end_time = serializers.DateTimeField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    value = serializers.IntegerField()

    def get_start_time(self, obj):
        flop_week, flop_weekday, flop_start_time = obj.week, obj.day, obj.start_time
        flop_day = Day(flop_weekday, flop_week)
        return flopdate_to_datetime(flop_day, flop_start_time)

    def get_end_time(self, obj):
        start_time = self.get_start_time(obj)
        duration = obj.duration
        return start_time + timedelta(seconds=duration * 60)


class UserPreferenceSerializer(PreferenceSerializer):
    user = serializers.CharField()

    class Meta:
        model = bm.UserPreference
        fields = '__all__'



class CoursePreferencesSerializer(PreferenceSerializer):
    class Meta:
        model = bm.CoursePreference
        fields = '__all__'


class RoomPreferencesSerializer(PreferenceSerializer):
    room = serializers.CharField(source='room.name')

    class Meta:
        model = bm.RoomPreference
        fields = '__all__'
