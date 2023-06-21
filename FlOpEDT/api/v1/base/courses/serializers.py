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
    course = serializers.IntegerField(source='course.id')
    module = serializers.IntegerField(source='course.module.id')
    tutor = serializers.IntegerField(source='tutor.id', allow_null=True)
    supp_tutors = serializers.SerializerMethodField()
    room = serializers.IntegerField(source='room.id', allow_null=True)
    # TODO V1: change into DatetimeFields
    # start_time = serializers.DatetimeField()
    # end_time = serializers.DateTimeField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    train_prog = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()    

    # Sructuration of the data
    class Meta:
        model = bm.ScheduledCourse
        fields = ['id', 'course', "module", 'tutor', 'supp_tutors', 'room', 'start_time', 'end_time', 'train_prog', 'groups']
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
    
    def get_groups(self, obj):
        return list(g.id for g in obj.course.groups.all())
    
    def get_supp_tutors(self, obj):
        return list(t.id for t in obj.course.supp_tutor.all())
    
    def get_train_prog(self, obj):
        return obj.course.groups.first().train_prog.id


class RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Room
        fields = '__all__'


class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Module
        fields = '__all__'