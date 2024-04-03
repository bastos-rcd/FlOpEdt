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
from typing import List

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

import base.models as bm

from api.v1.base.modification.serializers import TimetableVersionShortSerializer

#                             ------------------------------                            #
#                             ----Scheduled Courses (SC)----                            #
#                             ------------------------------                            #


class ScheduledCoursesSerializer(serializers.ModelSerializer):
    module_id = serializers.IntegerField(source="course.module.id")
    course_type_id = serializers.IntegerField(source="course.type.id")
    supp_tutors_ids = serializers.PrimaryKeyRelatedField(
        read_only=True, many=True, source="course.supp_tutors"
    )
    end_time = serializers.DateTimeField()
    number = serializers.IntegerField()
    train_prog_id = serializers.IntegerField(source="course.module.train_prog.id")
    group_ids = serializers.PrimaryKeyRelatedField(
        read_only=True, many=True, source="course.groups"
    )
    version = TimetableVersionShortSerializer()

    # Sructuration of the data
    class Meta:
        model = bm.ScheduledCourse
        fields = [
            "id",
            "course_id",
            "module_id",
            "course_type_id",
            "tutor_id",
            "supp_tutors_ids",
            "room_id",
            "start_time",
            "end_time",
            "train_prog_id",
            "group_ids",
            "number",
            "version",
        ]

    @classmethod
    def and_related(cls):
        return {
            "select": {"course": ["duration"], "version": ["id", "minor", "major"]},
            "prefetch": {},
        }


class RoomsSerializer(serializers.ModelSerializer):
    department_ids = serializers.SerializerMethodField()
    over_room_ids = serializers.SerializerMethodField()

    class Meta:
        model = bm.Room
        fields = ("id", "name", "over_room_ids", "department_ids")

    @extend_schema_field(List[OpenApiTypes.INT])
    def get_department_ids(self, obj):
        return [dep.id for dep in obj.departments.all()]

    @extend_schema_field(List[OpenApiTypes.INT])
    def get_over_room_ids(self, obj):
        return [over_room.id for over_room in obj.subroom_of.all()]


class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Module
        exclude = ("description", "ppn")


class ModulesFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Module
        fields = (
            "id",
            "name",
            "abbrev",
            "head_id",
            "train_prog_id",
            "training_period",
            "url",
            "description",
            "ppn",
        )


class TimetableVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TimetableVersion
        fields = ("id", "period_id", "major", "minor")
