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


#    --------------------------------------------------------------------------------
#   |                                                                                |
#   | ////////////////////////////////////////////////////////////////////////////// |
#   |                                                                                |
#   |                                     FETCHS                                     |
#   |                                                                                |
#   | ////////////////////////////////////////////////////////////////////////////// |
#   |                                                                                |
#    --------------------------------------------------------------------------------

#                             ------------------------------                            #
#                             ----Scheduled Courses (SC)----                            #
#                             ------------------------------                            #

class Tutor_Serializer(serializers.Serializer):
    username = serializers.CharField()

    class Meta:
        model = pm.Tutor
        fields = ['username']


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
        fields = ['id', 'name', 'train_prog','is_structural']


class Course_SC_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    room_type = serializers.CharField()
    week = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    groups = Group_SC_Serializer(many=True)
    supp_tutor = Tutor_Serializer(many=True)
    module = Module_SC_Serializer()
    pay_module = Module_SC_Serializer()
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
        fields = ['id', 'type', 'room_type', 'week', 'year', 'module', 'groups',
                  'is_graded', 'supp_tutor', 'pay_module']


class ScheduledCoursesSerializer(serializers.Serializer):
    # Spécification des champs voulus
    id = serializers.IntegerField()
    room = serializers.CharField(allow_null=True)
    start_time = serializers.IntegerField()
    day = serializers.CharField()
    course = Course_SC_Serializer()
    tutor = serializers.CharField(source='tutor.username', allow_null=True)
    id_visio = serializers.IntegerField(source='additional.link.id', allow_null=True)

    # Mise en forme des données
    class Meta:
        model = bm.ScheduledCourse
        fields = ['id', 'tutor', 'room', 'start_time', 'day', 'course', 'id_visio']



class ModuleCosmo_SC_Serializer(serializers.Serializer):
    name = serializers.CharField()
    abbrev = serializers.CharField()

    class Meta:
        model = bm.Module
        fields = ['name', 'abbrev']

class CourseCosmo_SC_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    room_type = serializers.CharField()
    week = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    groups = Group_SC_Serializer(many=True)
    module = Module_SC_Serializer()

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
        fields = ['id', 'type', 'room_type', 'week', 'year', 'module', 'groups', ]
        

class TutorDisplay_SC_Serializer(serializers.Serializer):
    color_bg = serializers.CharField()
    color_txt = serializers.CharField()

    class Meta:
        model = dwm.TutorDisplay
        fields = ['color_bg', 'color_txt']

class TutorCosmoSerializer(serializers.Serializer):
    username = serializers.CharField()
    display = TutorDisplay_SC_Serializer()

    class Meta:
        model = pm.Tutor
        fields = ['username', 'display']

class ScheduledCoursesCosmoSerializer(serializers.Serializer):
    # Spécification des champs voulus
    id = serializers.IntegerField()
    room = serializers.CharField()
    start_time = serializers.IntegerField()
    day = serializers.CharField()
    course = CourseCosmo_SC_Serializer()
    tutor = TutorCosmoSerializer()

    # Mise en forme des données
    class Meta:
        model = bm.ScheduledCourse
        fields = ['id', 'tutor', 'room', 'start_time', 'day', 'course']

#                             -------------------------------                           #
#                             ----UnscheduledCourses (PP)----                           #
#                             -------------------------------                           #


class ModuleDisplay_PP_Serializer(serializers.Serializer):
    color_bg = serializers.CharField()
    color_txt = serializers.CharField()

    class Meta:
        model = dwm.ModuleDisplay
        fields = ['color_bg', 'color_txt']


class Group_PP_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    train_prog = serializers.CharField()
    is_structural = serializers.BooleanField()
    
    class Meta:
        model = bm.GenericGroup
        fields = ['id', 'name', 'train_prog','is_structural']


class ModuleCours_PP_Serializer(serializers.Serializer):
    abbrev = serializers.CharField()
    display = ModuleDisplay_PP_Serializer()

    class Meta:
        model = bm.Module
        fields = ['abbrev', 'display']

class CourseType_PP_Serializer(serializers.Serializer):
    name = serializers.CharField()
    duration = serializers.IntegerField()

    class Meta:
        model = bm.CourseType
        fields = ['name', 'duration']


class UnscheduledCoursesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tutor = serializers.CharField()
    room_type = serializers.CharField()
    module = ModuleCours_PP_Serializer()
    groups = Group_PP_Serializer(many=True)
    type = CourseType_PP_Serializer()
    is_graded = serializers.BooleanField()
    supp_tutor = Tutor_Serializer(many=True)
    
    class Meta:
        model = bm.Course
        fields = ['id', 'tutor', 'room_type', 'module', 'groups', 'is_graded', 'supp_tutor']


#                                ---------------------------                            #
#                                ----Availabilities (Av)----                            #
#                                ---------------------------                            #



class AvailabilitiesSerializer(serializers.Serializer):
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    value = serializers.IntegerField()
    user = Tutor_Serializer()

    class Meta:
        model = bm.UserPreference
        fields = ['day', 'start_time', 'duration', 'value', 'user']


#                                  --------------------                                 #
#                                  ----Default Week----                                 #
#                                  --------------------                                 #


class DefaultWeekSerializer(serializers.Serializer):
    user = serializers.CharField()
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    value = serializers.IntegerField()

    class Meta:
        model = bm.UserPreference
        fields = ['user', 'day', 'start_time', 'duration', 'value']


#                              ---------------------------                              #
#                              ----Course Default Week----                              #
#                              ---------------------------                              #
#   No data to display


class CourseTypeDefaultWeekSerializer(serializers.Serializer):
    course_type = serializers.CharField()
    train_prog = serializers.CharField()
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    duration = serializers.IntegerField()
    value = serializers.IntegerField()

    class Meta:
        model = bm.CoursePreference
        fields = ['course_type', 'train_prog', 'day', 'start_time', 'duration', 'value']


#                                -------------------------                              #
#                                ----Unavailable rooms----                              #
#                                -------------------------                              #
# Has to be done in the views of base folder. Need to be clarified

#                                 -----------------------                               #
#                                 ----All Tutors (AT)----                               #
#                                 -----------------------                               #

class User_AT_Serializer(serializers.Serializer):
    username = serializers.CharField()

    class Meta:
        model = pm.User
        fields = ['username']


#                                  -------------------                                  #
#                                  ----Departments----                                  #
#                                  -------------------                                  #

class DepartmentAbbrevSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    abbrev = serializers.CharField()

    class Meta:
        model = bm.Department
        fields = ['id', 'abbrev']


#                                  --------------------                                 #
#                                  ----All Versions----                                 #
#                                  --------------------                                 #

class AllVersionsSerializer(serializers.ModelSerializer):
    # Spécification des champs voulus
    year = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    version = serializers.IntegerField()
    department = DepartmentAbbrevSerializer()

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

    # Mise en forme des données
    class Meta:
        model = bm.EdtVersion
        fields = ['year', 'week', 'version', 'department']


#                               --------------------------                              #
#                               ----Tutor Courses (TC)----                              #
#                               --------------------------                              #

class Department_TC_Serializer(serializers.Serializer):
    name = serializers.CharField()
    abbrev = serializers.CharField()

    class Meta:
        model = bm.Department
        fields = ['name', 'abbrev']


class CourseType_TC_Serializer(serializers.Serializer):
    department = Department_TC_Serializer()

    class Meta:
        model = bm.Course
        fields = ['department']


class Course_TC_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = CourseType_TC_Serializer()
    tutor = serializers.CharField()
    room_type = serializers.CharField()
    week = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    groups = Group_SC_Serializer()
    module = Module_SC_Serializer()

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
        fields = ['id', 'type', 'tutor', 'room_type', 'week', 'year', 'module', 'groups']


class TutorCourses_Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    room = serializers.CharField()
    start_time = serializers.IntegerField()
    course = Course_TC_Serializer()

    class Meta:
        model = bm.ScheduledCourse
        fields = ['room', 'start_time', 'course']





#                           -------------------------------------                       #
#                           ----Extra Scheduled Courses (ESC)----                       #
#                           -------------------------------------                       #


class CourseType_ESC_Serializer(serializers.Serializer):
    duration = serializers.IntegerField()
    department = DepartmentAbbrevSerializer()

    class Meta:
        model = bm.CourseType
        fields = ['duration', 'department']


class Course_ESC_Serializer(serializers.Serializer):
    tutor = serializers.CharField()
    type = CourseType_ESC_Serializer()

    class Meta:
        model = bm.Course
        fields = ['tutor', 'type']


class ExtraScheduledCoursesSerializer(serializers.Serializer):
    day = serializers.CharField()
    start_time = serializers.IntegerField()
    course = Course_ESC_Serializer()

    class Meta:
        model = bm.ScheduledCourse
        fields = ['day', 'start_time', 'course']


#                                  --------------------                                 #
#                                  ----Shared Rooms----                                 #
#                                  --------------------                                 #

#                                  ---------------------                                #
#                                  ----Breaking News----                                #
#                                  ---------------------                                #

class BKNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = dwm.BreakingNews
        fields = ['id', 'x_beg', 'x_end', 'y', 'txt', 'fill_color', 'strk_color', 'is_linked']


#                                     --------------                                    #
#                                     ----Decale----                                    #
#                                     --------------                                    #


#                                     --------------                                    #
#                                     ----Groups----                                    #
#                                     --------------                                    #

#                                      -------------                                    #
#                                      ----Rooms----                                    #
#                                      -------------                                    #

#                                  -------------------                                  #
#                                  ----Constraints----                                  #
#                                  -------------------                                  #

#                                   ------------------                                  #
#                                   ----Week infos----                                  #
#                                   ------------------                                  #

class IDTutorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.username

    class Meta:
        model = pm.Tutor
        fields = ['id', 'name']


class IDTrainProgSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TrainingProgramme
        fields = ['id', 'abbrev', 'name']


class IDModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Module
        fields = ['id', 'abbrev', 'name']


class IDCourseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.CourseType
        fields = ['id', 'name']


class IDGroupSerializer(serializers.ModelSerializer):
    train_prog = serializers.CharField()

    def get_train_ptorg(self, obj):
        return obj.train_prog.abbrev

    class Meta:
        model = bm.GenericGroup
        fields = ['id', 'name', 'train_prog']


class IDGroupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.GroupType
        fields = ['id', 'name'] 


class IDRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Room
        fields = ['id', 'name']


class IDRoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.RoomType
        fields = ['id', 'name']
