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

# -----------------
# -- PREFERENCES --
# -----------------


class UserAvailabilitySerializerV0(serializers.Serializer):
    user = serializers.CharField()
    week = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    value = serializers.IntegerField()

    def get_week(self, obj):
        if obj.week is not None:
            return obj.week.nb
        else:
            return

    def get_year(self, obj):
        if obj.week is not None:
            return obj.week.year
        else:
            return

    class Meta:
        model = bm.UserAvailability
        fields = ["user"]


class CourseAvailabilitySerializerV0(serializers.ModelSerializer):
    week = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    def get_week(self, obj):
        if obj.week is not None:
            return obj.week.nb
        else:
            return

    def get_year(self, obj):
        if obj.week is not None:
            return obj.week.year
        else:
            return

    class Meta:
        model = bm.CourseAvailability
        fields = "__all__"


class RoomAvailabilitySerializerV0(serializers.ModelSerializer):
    week = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    room = serializers.CharField(source="room.name")

    def get_week(self, obj):
        if obj.week is not None:
            return obj.week.nb
        else:
            return

    def get_year(self, obj):
        if obj.week is not None:
            return obj.week.year
        else:
            return

    class Meta:
        model = bm.RoomAvailability
        fields = "__all__"
