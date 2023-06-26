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
import displayweb.models as dwm
import people.models as pm
from base.timing import Day, flopdate_to_datetime
from datetime import timedelta
from api.base.courses.serializers import CoursesSerializer, Group_SC_Serializer, Module_SC_Serializer, Department_TC_Serializer

#                             ------------------------------                            #
#                             ----Scheduled Courses (SC)----                            #
#                             ------------------------------                            #



class ScheduledCoursesSerializer(serializers.Serializer):
    # Specification of wanted fields
    course_id = serializers.IntegerField(source='course.id')
    module_id = serializers.IntegerField(source='course.module.id')
    tutor_id = serializers.IntegerField(source='tutor.id', allow_null=True)
    supp_tutor_ids = serializers.SerializerMethodField()
    room_id = serializers.IntegerField(source='room.id', allow_null=True)
    # TODO V1: change into DatetimeFields
    # start_time = serializers.DatetimeField()
    # end_time = serializers.DateTimeField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    train_prog_id = serializers.SerializerMethodField()
    group_ids = serializers.SerializerMethodField()    

    # Sructuration of the data
    class Meta:
        model = bm.ScheduledCourse
        fields = ['id', 'course_id', 'module_id', 'tutor_id', 'supp_tutor_ids', 'room_id', 'start_time', 'end_time', 'train_prog_id', 'group_ids']
        ref_name = "New api scheduled course serializer"

    def get_start_time(self, obj):
        flop_week, flop_weekday, flop_start_time = obj.course.week, obj.day, obj.start_time
        flop_day = Day(flop_weekday, flop_week)
        return flopdate_to_datetime(flop_day, flop_start_time)

    def get_end_time(self, obj):
        start_time = self.get_start_time(obj)
        #TODO : duration should be in course instead of course type
        duration = obj.course.type.duration
        return start_time + timedelta(seconds=duration * 60)
    
    def get_group_ids(self, obj):
        return list(g.id for g in obj.course.groups.all())
    
    def get_supp_tutor_ids(self, obj):
        return list(t.id for t in obj.course.supp_tutor.all())
    
    def get_train_prog_id(self, obj):
        return obj.course.groups.first().train_prog.id


class RoomsSerializer(serializers.ModelSerializer):
    department_ids = serializers.SerializerMethodField()
    over_room_ids = serializers.SerializerMethodField()

    class Meta:
        model = bm.Room
        fields = ('id', 'name', 'over_room_ids', 'department_ids')

    def get_department_ids(self, obj):
        return [dep.id for dep in obj.departments.all()]
    
    def get_over_room_ids(self, obj):
        return [over_room.id for over_room in obj.subroom_of.all()]


class ModulesSerializer(serializers.ModelSerializer):
    head_id = serializers.IntegerField(source='head.id', allow_null=True)
    train_prog_id = serializers.IntegerField(source='train_prog.id')
    
    class Meta:
        model = bm.Module
        fields = ('id', 'name', 'abbrev','head_id', 'train_prog_id', 'description')