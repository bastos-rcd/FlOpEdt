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
import displayweb.models as dwm
from api.base.serializers import TrainingProgramsSerializer

from rest_framework import serializers

class Department_TC_Serializer(serializers.Serializer):
    name = serializers.CharField()
    abbrev = serializers.CharField()
    id = serializers.IntegerField()

    class Meta:
        model = bm.Department
        fields = ['name', 'abbrev', 'id']

class CourseTypeSimpleSerializer(serializers.Serializer):
    department = Department_TC_Serializer()
    name = serializers.CharField()
    duration = serializers.IntegerField()

    class Meta:
        model = bm.CourseType
        fields = ['name', 'department', 'duration']

class ModuleDisplay_SC_Serializer(serializers.Serializer):
    color_bg = serializers.CharField()
    color_txt = serializers.CharField()

    class Meta:
        model = dwm.ModuleDisplay
        fields = ['color_bg', 'color_txt']

class Module_SC_Serializer(serializers.Serializer):
    name = serializers.CharField()
    abbrev = serializers.CharField()
    display = ModuleDisplay_SC_Serializer()

    class Meta:
        model = bm.Module
        fields = ['name', 'abbrev', 'display']

class Group_SC_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    train_prog = serializers.CharField()
    name = serializers.CharField()
    is_structural = serializers.BooleanField()

    class Meta:
        model = bm.GenericGroup
        fields = ['id', 'name', 'train_prog', 'is_structural']

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
    department = Department_TC_Serializer()
    name = serializers.CharField()
    duration = serializers.IntegerField()

    class Meta:
        model = bm.CourseType
        fields = ['name', 'department', 'duration']

class RoomType_SC_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.RoomType
        fields = ['name']

class RoomType_C_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.RoomType
        fields = ['name']


class Group_C_Serializer(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        model = bm.StructuralGroup
        fields = ['name']


class Module_C_Serializer(serializers.Serializer):
    abbrev = serializers.CharField()

    class Meta:
        model = bm.Module
        fields = ['abbrev']


class CoursesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = CourseTypeSimpleSerializer()
    room_type = RoomType_SC_Serializer()
    week = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    groups = Group_SC_Serializer(many=True)
    tutor = serializers.CharField()
    supp_tutor = serializers.CharField()
    module = Module_SC_Serializer()
    modulesupp = Module_C_Serializer()
    pay_module = Module_C_Serializer()
    is_graded = serializers.BooleanField()

    def get_week(self, obj):
        if(obj.week is not None):
            return (obj.week.nb)
        else:
            return

    def get_year(self, obj):
        if(obj.week is not None):
            return (obj.week.year)
        else:
            return
            
    class Meta:
        model = bm.Course
        fields = ['id', 'week', 'year', 'department', 'type',
                  'room_type', 'tutor', 'supp_tutor', 'groups', 'module', 'modulesupp', 'pay_module']



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

