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
from django.contrib.auth.admin import UserAdmin

from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import resources, fields

from base.admin import DepartmentModelAdminMixin

from people.models import User, Tutor, FullStaff, SupplyStaff, BIATOS, Student,\
    UserDepartmentSettings, StudentPreferences, GroupPreferences, UserPreferredLinks,\
    PhysicalPresence



class UserDepartmentInline(admin.TabularInline):
    model = User.departments.through


class UserModelAdmin(DepartmentModelAdminMixin, UserAdmin):

    inlines = [
        UserDepartmentInline,
    ]

    readonly_fields= ('last_login', 'date_joined',)

    def get_inline_instances(self, request, obj=None):
        """
        This hooks is used to hide department edition 
        when a department admin session is active
        """
        instances = super().get_inline_instances(request, obj)

        if hasattr(request, 'department'):
            instances = [i for i in instances if not isinstance(i, UserDepartmentInline)]
                
        return instances

    def get_department_lookup(self, department):
        """
        Hook for overriding default department lookup research
        """
        return {'departments': department}

    def save_model(self, request, obj, form, change):
        #
        # Associate the current department as the main one for the created user
        #
        super().save_model(request, obj, form, change)

        if hasattr(request, 'department') and not change:
            UserDepartmentSettings.objects.create(
                department=request.department, user=obj, is_main=True)

    def get_fieldsets(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        fieldsets = list(super().get_fieldsets(request, obj))
        updated_fieldsets = []
        # Remove Permissions fieldsets for non superuser
        if not request.user.is_superuser:
            for fs in fieldsets:
                if not fs[0] == 'Permissions':
                    updated_fieldsets.append(fs)

            fieldsets = list(updated_fieldsets)
        return tuple(fieldsets)

    class Meta:
        app_label = 'auth'


class TutorResource(resources.ModelResource):

    class Meta:
        model = Tutor
        fields = ("username", "first_name", "last_name", "email")


class StudentPreferencesResource(resources.ModelResource):

    student_username = fields.Field(column_name='student_username',
                                    attribute='student',
                                    widget=ForeignKeyWidget('Student', 'username'))

    student_group = fields.Field(column_name='student_group',
                                 attribute='student',
                                 widget=ForeignKeyWidget('Student', 'generic_groups'))

    class Meta:
        model = StudentPreferences
        fields = ("student_username", "student_group",
                  "morning_weight", "free_half_day_weight")


class GroupPreferencesResource(resources.ModelResource):

    train_prog = fields.Field(column_name='train_prog',
                              attribute='group',
                              widget=ForeignKeyWidget('Group', 'train_prog'))

    group = fields.Field(column_name='group_name',
                         attribute='group',
                         widget=ForeignKeyWidget('Group', 'name'))

    class Meta:
        model = GroupPreferences
        fields = ("train_prog", "group", "morning_weight",
                  "free_half_day_weight")


class UserPreferredLinksResource(resources.ModelResource):
    links = fields.Field(column_name='links',
                         attribute='links',
                         widget=ManyToManyWidget('base.Enrichedlink',
                                                 field='concatenated',
                                                 separator='|'))
    user = fields.Field(column_name='user',
                        attribute='user',
                        widget=ForeignKeyWidget('people.User', 'username'))
    class Meta:
        model = UserPreferredLinks
        fields = ('user', 'links')


class UserPreferredLinksAdmin(admin.ModelAdmin):
    pass


class PhysicalPresenceResource(resources.ModelResource):
    user = fields.Field(column_name='user',
                        attribute='user',
                        widget=ForeignKeyWidget('people.User', 'username'))

    class Meta:
        model = PhysicalPresence
        fields = ('user', 'day', 'week', 'year')
    


admin.site.register(FullStaff, UserModelAdmin)
admin.site.register(SupplyStaff, UserModelAdmin)
admin.site.register(BIATOS, UserModelAdmin)
admin.site.register(Student, UserModelAdmin)
admin.site.register(User, UserModelAdmin)
admin.site.register(UserPreferredLinks, UserPreferredLinksAdmin)
