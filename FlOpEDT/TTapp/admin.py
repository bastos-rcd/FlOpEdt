# -*- coding: utf-8 -*-

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




from django.contrib import admin
from base.admin import DepartmentModelAdmin

from import_export import resources, fields
from import_export.widgets import ManyToManyWidget

from TTapp.models import \
    LimitModulesTimePerPeriod, Stabilize, \
    MinModulesHalfDays, MinTutorsHalfDays, MinGroupsHalfDays,\
    MinNonPreferedTrainProgsSlot, MinNonPreferedTutorsSlot, \
    CustomConstraint, SimultaneousCourses, MinimizeBusyDays, RespectBoundPerDay,\
    AvoidBothTimes, LimitedRoomChoices, LimitedStartTimeChoices, \
    LimitTutorsTimePerPeriod, LimitGroupsTimePerPeriod, LowerBoundBusyDays, GroupsLunchBreak, BreakAroundCourseType, \
    NoVisio, LimitGroupsPhysicalPresence, BoundPhysicalPresenceHalfDays, TutorsLunchBreak, VisioOnly, NoCourseOnDay

from TTapp.TTConstraints.orsay_constraints import GroupsLunchBreak

# Register your models here.

from FlOpEDT.filters import DropdownFilterAll, DropdownFilterRel, \
    DropdownFilterCho
from django.conf import settings


class CustomConstraintAdmin(DepartmentModelAdmin):
    list_display = ('class_name', 
                'week', 
                'year',
                'comment')
    ordering = ()
    list_filter = (('groups', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   ('modules', DropdownFilterRel),
                   )   


class LimitModulesTimePerPeriodAdmin(DepartmentModelAdmin):
    list_display = ('week', 
                    'year',
                    'course_type',
                    'max_hours',
                    'period', 
                    'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('modules', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )

class LimitGroupsTimePerPeriodAdmin(DepartmentModelAdmin):
    list_display = ('week',
                    'year',
                    'course_type',
                    'max_hours',
                    'period',
                    'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )

class LimitTutorsTimePerPeriodAdmin(DepartmentModelAdmin):
    list_display = ('week',
                    'year',
                    'course_type',
                    'max_hours',
                    'period',
                    'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )

class ReasonableDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   )


class StabilizeAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'general',
                    'group', 'tutor', 'module', 'course_type', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class MinTutorsHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'join2courses', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   'join2courses',
                   )


class MinModulesHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('modules', DropdownFilterRel),
                   )


class MinGroupsHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   )

    
    def get_field_queryset(self, db, db_field, request):

        queryset = super().get_field_queryset(db, db_field, request)

        if queryset and db_field.name == 'groups':
            return queryset.filter(basic=True).distinct()

        return queryset                          


class MinNonPreferedTutorsSlotAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   )

class MinNonPreferedTrainProgsSlotAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   )


class AvoidBothTimesAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'tutor', 'group', 'time1', 'time2', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('time1', DropdownFilterRel),
                   ('time2', DropdownFilterRel),
                   )


class SimultaneousCoursesAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('courses', DropdownFilterRel),
                   )


class RespectBoundPerDayAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   )


class MinimizeBusyDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   )


class LimitedRoomChoicesAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'group', 'tutor', 'module', 'course_type',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class LimitedStartTimeChoicesAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'group', 'tutor', 'module', 'course_type', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class LowerBoundBusyDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'tutor', 'min_days_nb', 'lower_bound_hours', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   )


class GroupsLunchBreakAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )


class TutorsLunchBreakAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   )

class BreakAroundCourseTypeAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )


class NoVisioAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )


class VisioOnlyAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )


class BoundPhysicalPresenceHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )


class LimitGroupsPhysicalPresenceAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   )


class GroupsLunchBreakResource(resources.ModelResource):
    groups = fields.Field(
        column_name='groups',
        attribute='groups',
        widget=ManyToManyWidget('base.Group', field='full_name', separator='|'))

    class Meta:
        model = GroupsLunchBreak
        fields = ('start_time', 'end_time', 'lunch_length', 'groups')


class NoCourseOnDayAdmin(DepartmentModelAdmin):
    list_display = ('week',
                    'year',
                    'weekday',
                    'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )

    
admin.site.register(CustomConstraint, CustomConstraintAdmin)
admin.site.register(Stabilize, StabilizeAdmin)
admin.site.register(MinGroupsHalfDays, MinGroupsHalfDaysAdmin)
admin.site.register(MinTutorsHalfDays, MinTutorsHalfDaysAdmin)
admin.site.register(MinModulesHalfDays, MinModulesHalfDaysAdmin)
admin.site.register(MinNonPreferedTutorsSlot, MinNonPreferedTutorsSlotAdmin)
admin.site.register(MinNonPreferedTrainProgsSlot, MinNonPreferedTrainProgsSlotAdmin)
# admin.site.register(AvoidBothTimes, AvoidBothTimesAdmin)
admin.site.register(SimultaneousCourses, SimultaneousCoursesAdmin)
admin.site.register(MinimizeBusyDays, MinimizeBusyDaysAdmin)
admin.site.register(RespectBoundPerDay, RespectBoundPerDayAdmin)
admin.site.register(LimitedStartTimeChoices, LimitedStartTimeChoicesAdmin)
admin.site.register(LimitedRoomChoices, LimitedRoomChoicesAdmin)
admin.site.register(LimitModulesTimePerPeriod, LimitModulesTimePerPeriodAdmin)
admin.site.register(LimitGroupsTimePerPeriod, LimitGroupsTimePerPeriodAdmin)
admin.site.register(LimitTutorsTimePerPeriod, LimitTutorsTimePerPeriodAdmin)
admin.site.register(LowerBoundBusyDays, LowerBoundBusyDaysAdmin)
admin.site.register(GroupsLunchBreak, GroupsLunchBreakAdmin)
admin.site.register(TutorsLunchBreak, TutorsLunchBreakAdmin)
admin.site.register(BreakAroundCourseType, BreakAroundCourseTypeAdmin)
admin.site.register(NoCourseOnDay, NoCourseOnDayAdmin)

if settings.VISIO_MODE:
    admin.site.register(NoVisio, NoVisioAdmin)
    admin.site.register(VisioOnly, VisioOnlyAdmin)
    admin.site.register(BoundPhysicalPresenceHalfDays, BoundPhysicalPresenceHalfDaysAdmin)
    admin.site.register(LimitGroupsPhysicalPresence, LimitGroupsPhysicalPresenceAdmin)

