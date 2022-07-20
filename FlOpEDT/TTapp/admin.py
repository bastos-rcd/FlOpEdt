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
    LimitModulesTimePerPeriod, StabilizeTutorsCourses, StabilizeGroupsCourses, \
    MinModulesHalfDays, MinTutorsHalfDays, MinGroupsHalfDays,\
    MinNonPreferedTrainProgsSlot, MinNonPreferedTutorsSlot, \
    CustomConstraint, SimultaneousCourses, MinimizeBusyDays, RespectMaxHoursPerDay, RespectMinHoursPerDay, \
    LimitedRoomChoices, LimitedStartTimeChoices, LimitCourseTypeTimePerPeriod, \
    LimitTutorsTimePerPeriod, LimitGroupsTimePerPeriod, LowerBoundBusyDays, BreakAroundCourseType, \
    NoVisio, LimitGroupsPhysicalPresence, BoundPhysicalPresenceHalfDays, TutorsLunchBreak, VisioOnly, \
    NoTutorCourseOnDay, NoGroupCourseOnDay, \
    ConsiderDependencies, ConsiderPivots, NoSimultaneousGroupCourses, ScheduleAllCourses, AssignAllCourses, \
    ConsiderTutorsUnavailability, LimitHoles, \
    Curfew, \
    ModulesByBloc, LimitTutorTimePerWeeks, LimitUndesiredSlotsPerWeek, LimitSimultaneousCoursesNumber, \
    LocateAllCourses, LimitGroupMoves, LimitTutorMoves, ConsiderRoomSorts


from TTapp.TTConstraints.orsay_constraints import GroupsLunchBreak

# Register your models here.

from core.filters import DropdownFilterAll, DropdownFilterRel


class BasicConstraintAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('weeks__nb', DropdownFilterAll))


class CustomConstraintAdmin(DepartmentModelAdmin):
    list_display = ('class_name',
                    'comment')
    ordering = ()
    list_filter = (('groups', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   ('modules', DropdownFilterRel),
                   )   

class BasicTutorsConstraintAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('tutors', DropdownFilterRel),
                   ('weeks__nb', DropdownFilterAll))

class LimitModulesTimePerPeriodAdmin(DepartmentModelAdmin):
    list_display = ('course_type',
                    'max_hours',
                    'period', 
                    'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('weeks__nb', DropdownFilterAll),
                   ('modules', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class LimitGroupsTimePerPeriodAdmin(DepartmentModelAdmin):
    list_display = ('course_type',
                    'max_hours',
                    'period',
                    'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('weeks__nb', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class LimitTutorsTimePerPeriodAdmin(DepartmentModelAdmin):
    list_display = ('course_type',
                    'max_hours',
                    'period',
                    'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('weeks__nb', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class ReasonableDaysAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('train_progs', DropdownFilterRel),
                   ('weeks__nb', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   )


class StabilizeTutorsCoursesAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   )

class StabilizeGroupsCoursesAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )


class MinTutorsHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('join2courses', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   'join2courses',
                   )


class MinModulesHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('modules', DropdownFilterRel),
                   )


class MinGroupsHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   )

    def get_field_queryset(self, db, db_field, request):

        queryset = super().get_field_queryset(db, db_field, request)

        if queryset and db_field.name == 'groups':
            return queryset.filter(basic=True).distinct()

        return queryset                          



class AvoidBothTimesAdmin(DepartmentModelAdmin):
    list_display = ('tutor', 'group', 'time1', 'time2', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('time1', DropdownFilterRel),
                   ('time2', DropdownFilterRel),
                   )


class CoursesAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('courses', DropdownFilterRel),
                   )


class LimitRoomChoicesAdmin(DepartmentModelAdmin):
    list_display = ('group', 'tutor', 'module', 'course_type',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('group', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class LimitedStartTimeChoicesAdmin(DepartmentModelAdmin):
    list_display = ('group', 'tutor', 'module', 'course_type', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   ('course_type', DropdownFilterRel),
                   )


class LowerBoundBusyDaysAdmin(DepartmentModelAdmin):
    list_display = ('tutor', 'min_days_nb', 'lower_bound_hours', 'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   )


class GroupsLunchBreakAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )


class GroupsConstraintAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('groups', DropdownFilterRel),
                   )


class GroupsLunchBreakResource(resources.ModelResource):
    groups = fields.Field(
        column_name='groups',
        attribute='groups',
        widget=ManyToManyWidget('base.StructuralGroup', field='full_name', separator='|'))

    class Meta:
        model = GroupsLunchBreak
        fields = ('start_time', 'end_time', 'lunch_length', 'groups')


class NoCourseOnDayAdmin(DepartmentModelAdmin):
    list_display = ('weekday',
                    'comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   )


class ConsiderDependenciesAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('modules', DropdownFilterRel),
                   )


class ConsiderPivotsAdmin(DepartmentModelAdmin):
    list_display = ('comment',
                    'weight',
                    'is_active')
    ordering = ()
    list_filter = (('weeks__nb', DropdownFilterAll),
                   ('train_progs', DropdownFilterRel),
                   ('modules', DropdownFilterRel),
                   )



admin.site.register(ConsiderDependencies, ConsiderDependenciesAdmin)
admin.site.register(ConsiderPivots, ConsiderPivotsAdmin)
admin.site.register(CustomConstraint, CustomConstraintAdmin)
admin.site.register(StabilizeTutorsCourses, StabilizeTutorsCoursesAdmin)
admin.site.register(StabilizeGroupsCourses, StabilizeGroupsCoursesAdmin)
admin.site.register(MinGroupsHalfDays, MinGroupsHalfDaysAdmin)
admin.site.register(MinTutorsHalfDays, MinTutorsHalfDaysAdmin)
admin.site.register(MinModulesHalfDays, MinModulesHalfDaysAdmin)
admin.site.register(MinNonPreferedTutorsSlot, BasicTutorsConstraintAdmin)
admin.site.register(MinNonPreferedTrainProgsSlot, BasicConstraintAdmin)
admin.site.register(SimultaneousCourses, CoursesAdmin)
admin.site.register(MinimizeBusyDays, BasicTutorsConstraintAdmin)
admin.site.register(RespectMaxHoursPerDay, BasicTutorsConstraintAdmin)
admin.site.register(RespectMinHoursPerDay, BasicTutorsConstraintAdmin)
admin.site.register(LimitedStartTimeChoices, LimitedStartTimeChoicesAdmin)
admin.site.register(LimitedRoomChoices, LimitRoomChoicesAdmin)
admin.site.register(LimitModulesTimePerPeriod, LimitModulesTimePerPeriodAdmin)
admin.site.register(LimitGroupsTimePerPeriod, LimitGroupsTimePerPeriodAdmin)
admin.site.register(LimitTutorsTimePerPeriod, LimitTutorsTimePerPeriodAdmin)
admin.site.register(LimitCourseTypeTimePerPeriod, BasicConstraintAdmin)
admin.site.register(LowerBoundBusyDays, LowerBoundBusyDaysAdmin)
admin.site.register(GroupsLunchBreak, GroupsLunchBreakAdmin)
admin.site.register(TutorsLunchBreak, BasicTutorsConstraintAdmin)
admin.site.register(BreakAroundCourseType, GroupsConstraintAdmin)
admin.site.register(NoGroupCourseOnDay, NoCourseOnDayAdmin)
admin.site.register(NoTutorCourseOnDay, NoCourseOnDayAdmin)
admin.site.register(Curfew, BasicConstraintAdmin)
admin.site.register(NoVisio, GroupsConstraintAdmin)
admin.site.register(VisioOnly, GroupsConstraintAdmin)
admin.site.register(BoundPhysicalPresenceHalfDays, GroupsConstraintAdmin)
admin.site.register(LimitGroupsPhysicalPresence, BasicConstraintAdmin)
admin.site.register(NoSimultaneousGroupCourses, BasicConstraintAdmin)
admin.site.register(ScheduleAllCourses, BasicConstraintAdmin)
admin.site.register(AssignAllCourses, BasicConstraintAdmin)
admin.site.register(ConsiderTutorsUnavailability, BasicConstraintAdmin)
admin.site.register(LimitHoles, BasicConstraintAdmin)
admin.site.register(LimitTutorTimePerWeeks, BasicConstraintAdmin)
admin.site.register(ModulesByBloc, BasicConstraintAdmin)
admin.site.register(LimitUndesiredSlotsPerWeek, BasicConstraintAdmin)
admin.site.register(LimitSimultaneousCoursesNumber, BasicConstraintAdmin)
admin.site.register(LocateAllCourses, BasicConstraintAdmin)
admin.site.register(LimitTutorMoves, BasicConstraintAdmin)
admin.site.register(LimitGroupMoves, BasicConstraintAdmin)
admin.site.register(ConsiderRoomSorts, BasicConstraintAdmin)


