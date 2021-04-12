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

import base.models as bm
from api.base.serializers import TrainingProgramsSerializer

from rest_framework import serializers

class TrainingPrograms_M_Serializer(serializers.Serializer):
    abbrev = serializers.CharField()

    class Meta:
        model = bm.TrainingProgramme
        fields = ['abbrev', ]


class Period_M_Serializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Period
        fields = ['starting_week', 'ending_week', 'name']


class ModuleFullSerializer(serializers.ModelSerializer):
    train_prog = TrainingProgramsSerializer()
    period = Period_M_Serializer()

    class Meta:
        model = bm.Module
        fields = ['name', 'abbrev', 'head', 'ppn', 'url', 'train_prog', 'period']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Module
        fields = ['name', 'abbrev', 'url']


class Department_Name_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.Department
        fields = ['name']


class CourseType_C_Serializer(serializers.Serializer):
    department = Department_Name_Serializer()
    name = serializers.CharField()

    class Meta:
        model = bm.CourseType
        fields = ['name', 'department']


class RoomType_C_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.RoomType
        fields = ['name']


class Group_C_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.Group
        fields = ['name']


class Module_C_Serializer(serializers.Serializer):
    abbrev = serializers.CharField()

    class Meta:
        model = bm.Module
        fields = ['abbrev']


class CoursesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    week = serializers.IntegerField()
    year = serializers.IntegerField()
    no = serializers.IntegerField()
    type = CourseType_C_Serializer()
    room_type = RoomType_C_Serializer()
    tutor = serializers.CharField()
    supp_tutor = serializers.CharField()
    group = Group_C_Serializer()
    module = Module_C_Serializer()
    modulesupp = Module_C_Serializer()

    class Meta:
        model = bm.Course
        fields = ['id', 'week', 'year', 'no', 'department', 'type',
                  'room_type', 'tutor', 'supp_tutor', 'group', 'module', 'modulesupp']



class CourseTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = bm.CourseType
        fields = ['name', 'duration']


class CourseTypeNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = bm.CourseType
        fields = ['name']

