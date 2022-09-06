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
import logging

from core.department import get_model_department_lookup

from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields import related as related_fields

from django.contrib import admin
import django.contrib.auth as auth

from django.utils.translation import gettext_lazy as _

from people.models import Tutor, User
from base.models import CourseStartTimeConstraint, StructuralGroup, TransversalGroup, \
    Room, Module, Course, \
    UserPreference, ScheduledCourse, EdtVersion, CourseModification, \
    TrainingProgramme, Regen, Holiday, TrainingHalfDay, \
    CoursePreference, Dependency, Department, CourseType, \
    ScheduledCourseAdditional, CourseAdditional, RoomPreference, RoomSort, RoomType, EnrichedLink, GroupPreferredLinks, \
    Mode, Period
from displayweb.models import ModuleDisplay
from displayweb.models import TutorDisplay
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from core.filters import DropdownFilterAll, DropdownFilterRel, \
    DropdownFilterSimple

logger = logging.getLogger('admin')


# from core.models import Book

# class ProfResource(resources.ModelResource):
#
#    class Meta:
#        model = Prof
#        # fields = ('abbrev',)

# <editor-fold desc="RESOURCES">
# -----------------
# -- PREFERENCES --
# -----------------

class CoursPlaceResource(resources.ModelResource):
    id = fields.Field(column_name='id_course',
                      attribute='course',
                      widget=ForeignKeyWidget(Course, 'id'))
    no = fields.Field(column_name='num_course',
                      attribute='course',
                      widget=ForeignKeyWidget(Course, 'no'))
    prof = fields.Field(column_name='prof_name',
                        attribute='tutor',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    # prof_first_name = fields.Field(column_name='prof_first_name',
    #                                attribute='cours__tutor',
    #                                widget=ForeignKeyWidget(Tutor,
    #                                 'first_name'))
    # prof_last_name = fields.Field(column_name='prof_last_name',
    #                               attribute='cours__tutor',
    #                               widget=ForeignKeyWidget(Tutor, 'last_name'))
    groups = fields.Field(column_name='gpe_name',
                          attribute='course__groups',
                          widget=ManyToManyWidget(StructuralGroup, field='name',
                                                  separator='|'))
    promo = fields.Field(column_name='gpe_promo',
                         attribute='course__module__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    module = fields.Field(column_name='module',
                          attribute='course__module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    coursetype = fields.Field(column_name='coursetype',
                              attribute='course__type',
                              widget=ForeignKeyWidget(CourseType, 'name'))
    # day = fields.Field(column_name='day',
    #                     attribute='day',
    #                     widget=ForeignKeyWidget(Day, 'no'))
    # salle = fields.Field(column_name = 'salle',
    #                      attribute = 'salle',
    #                      widget = ForeignKeyWidget(Salle,'nom'))
    room = fields.Field(column_name='room',
                        attribute='room',
                        widget=ForeignKeyWidget(Room, 'name'))
    room_type = fields.Field(column_name='room_type',
                             attribute='course__room_type',
                             widget=ForeignKeyWidget(RoomType, 'name'))
    color_bg = fields.Field(column_name='color_bg',
                            attribute='course__module__display',
                            widget=ForeignKeyWidget(ModuleDisplay, 'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                             attribute='course__module__display',
                             widget=ForeignKeyWidget(ModuleDisplay,
                                                     'color_txt'))
    id_visio = fields.Field(column_name='id_visio',
                            attribute='additional__link',
                            widget=ForeignKeyWidget(EnrichedLink,
                                                    'id'))
    comment = fields.Field(column_name='comment',
                           attribute='additional',
                           widget=ForeignKeyWidget(ScheduledCourseAdditional,
                                                   'comment'))
    allow_visio = fields.Field(column_name='allow_visio',
                               attribute='course__additional',
                               widget=ForeignKeyWidget(
                                   CourseAdditional,
                                   'visio_preference_value'))
    is_graded = fields.Field(column_name='graded',
                             attribute='course',
                             widget=ForeignKeyWidget(Course, 'is_graded'))

    class Meta:
        model = ScheduledCourse
        fields = ('id', 'no', 'groups', 'promo', 'color_bg', 'color_txt',
                  'module', 'coursetype', 'day', 'start_time',
                  'week', 'room', 'prof', 'room_type',
                  'id_visio', 'comment', 'allow_visio', 'is_graded')


class CoursPlaceResourceCosmo(resources.ModelResource):
    id = fields.Field(column_name='id_course',
                      attribute='course',
                      widget=ForeignKeyWidget(Course, 'id'))
    no = fields.Field(column_name='num_course',
                      attribute='course',
                      widget=ForeignKeyWidget(Course, 'no'))
    prof = fields.Field(column_name='prof_name',
                        attribute='tutor',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    # prof_first_name = fields.Field(column_name='prof_first_name',
    #                                attribute='cours__tutor',
    #                                widget=ForeignKeyWidget(Tutor,
    #                                 'first_name'))
    # prof_last_name = fields.Field(column_name='prof_last_name',
    #                               attribute='cours__tutor',
    #                               widget=ForeignKeyWidget(Tutor, 'last_name'))
    groups = fields.Field(column_name='gpe_name',
                          attribute='course__groups',
                          widget=ManyToManyWidget(StructuralGroup, field='name',
                                                  separator='|'))
    promo = fields.Field(column_name='gpe_promo',
                         attribute='course__module__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    module = fields.Field(column_name='module',
                          attribute='course__module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    coursetype = fields.Field(column_name='coursetype',
                              attribute='course__type',
                              widget=ForeignKeyWidget(CourseType, 'name'))
    # salle = fields.Field(column_name = 'salle',
    #                      attribute = 'salle',
    #                      widget = ForeignKeyWidget(Salle,'nom'))
    room = fields.Field(column_name='room',
                        attribute='room',
                        widget=ForeignKeyWidget(Room, 'name'))
    color_bg = fields.Field(column_name='color_bg',
                            attribute='tutor__display',
                            widget=ForeignKeyWidget(TutorDisplay, 'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                             attribute='tutor__display',
                             widget=ForeignKeyWidget(TutorDisplay, 'color_txt'))
    id_visio = fields.Field(column_name='id_visio',
                            attribute='additional__link',
                            widget=ForeignKeyWidget(EnrichedLink,
                                                    'id'))
    comment = fields.Field(column_name='comment',
                           attribute='additional',
                           widget=ForeignKeyWidget(ScheduledCourseAdditional,
                                                   'comment'))
    is_graded = fields.Field(column_name='graded',
                             attribute='course',
                             widget=ForeignKeyWidget(Course, 'is_graded'))

    class Meta:
        model = ScheduledCourse
        fields = ('id', 'no', 'groups', 'promo', 'color_bg', 'color_txt',
                  'module', 'day', 'start_time', 'week', 'room', 'prof',
                  'id_visio', 'comment', 'is_graded')


class TutorCoursesResource(CoursPlaceResource):
    department = fields.Field(column_name='dept',
                              attribute='course__type__department',
                              widget=ForeignKeyWidget(Department, 'abbrev'))

    class Meta:
        model = ScheduledCourse
        fields = ('id', 'no', 'groups', 'promo', 'color_bg', 'color_txt',
                  'module', 'coursetype', 'day', 'start_time',
                  'week', 'room', 'prof', 'room_type', 'department')


class MultiDepartmentTutorResource(resources.ModelResource):
    tutor = fields.Field(column_name='tutor',
                         attribute='course__tutor',
                         widget=ForeignKeyWidget(Tutor, 'username'))
    department = fields.Field(column_name='department',
                              attribute='course__type__department',
                              widget=ForeignKeyWidget(Department, 'abbrev'))
    duration = fields.Field(column_name='duration',
                            attribute='course__type__duration')

    class Meta:
        model = ScheduledCourse
        fields = ('tutor', 'department', 'day', 'start_time', 'duration')


class SharedRoomsResource(resources.ModelResource):
    room = fields.Field(column_name='room',
                        attribute='room',
                        widget=ForeignKeyWidget(Room, 'name'))
    department =  fields.Field(column_name='department',
                               attribute='course__type__department',
                               widget=ForeignKeyWidget(Department, 'abbrev'))
    duration = fields.Field(column_name='duration',
                            attribute='course__type__duration')

    class Meta:
        model = ScheduledCourse
        fields = ('room', 'department', 'day', 'start_time', 'duration')


class CoursResource(resources.ModelResource):
    promo = fields.Field(column_name='promo',
                         attribute='module__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    prof = fields.Field(column_name='prof',
                        attribute='tutor',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    module = fields.Field(column_name='module',
                          attribute='module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    coursetype = fields.Field(column_name='coursetype',
                              attribute='type',
                              widget=ForeignKeyWidget(CourseType, 'name'))
    duration = fields.Field(column_name='duration',
                            attribute='course__type__duration')
    groups = fields.Field(column_name='groups',
                         attribute='groups',
                         widget=ManyToManyWidget(StructuralGroup, field='name',
                                                 separator='|'))
    color_bg = fields.Field(column_name='color_bg',
                            attribute='module__display',
                            widget=ForeignKeyWidget(ModuleDisplay,
                                                    'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                             attribute='module__display',
                             widget=ForeignKeyWidget(ModuleDisplay,
                                                     'color_txt'))
    room_type = fields.Field(column_name='room_type',
                             attribute='room_type',
                             widget=ForeignKeyWidget(RoomType, 'name'))
    allow_visio = fields.Field(column_name='allow_visio',
                               attribute='additional',
                               widget=ForeignKeyWidget(
                                   CourseAdditional,
                                   'visio_preference_value'
                               ))

    class Meta:
        model = Course
        fields = ('id', 'no', 'tutor_name', 'groups', 'promo', 'module',
                  'coursetype', 'color_bg', 'color_txt', 'prof', 'room_type',
                  'allow_visio','is_graded')


class SemaineAnResource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ("week", "year")


class DispoResource(resources.ModelResource):
    prof = fields.Field(attribute='user',
                        widget=ForeignKeyWidget(User, 'username'))

    class Meta:
        model = UserPreference
        fields = ('day', 'start_time', 'duration', 'value', 'prof')


class AllDispoResource(resources.ModelResource):
    prof = fields.Field(attribute='user',
                        widget=ForeignKeyWidget(User, 'username'))

    class Meta:
        model = UserPreference
        fields = ('year', 'week', 'day', 'start_time', 'duration', 'value',
                  'prof')


class CoursePreferenceResource(resources.ModelResource):
    type_name = fields.Field(attribute='course_type',
                             widget=ForeignKeyWidget(CourseType, 'name'))
    train_prog = fields.Field(attribute='train_prog',
                              widget=ForeignKeyWidget(TrainingProgramme,
                                                      'abbrev'))

    class Meta:
        model = CoursePreference
        fields = ('type_name', 'train_prog', 'day', 'start_time', 'duration',
                  'value')


class UnavailableRoomsResource(resources.ModelResource):
    class Meta:
        model = RoomPreference
        fields = ("room", "day", "start_time", "duration")


class RoomPreferenceResource(resources.ModelResource):
    room = fields.Field(attribute='room',
                        widget=ForeignKeyWidget(Room, 'name'))

    class Meta:
        model = RoomPreference
        fields = ("room", "day", "start_time", "duration", "value")


class VersionResource(resources.ModelResource):
    class Meta:
        model = EdtVersion;
        fields = ("year", "week", "version", "department")


class ModuleRessource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ('module__abbrev', 'module__name', 'module__url')


class TutorRessource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ('tutor__username', 'tutor__first_name', 'tutor__last_name',
                  'tutor__email')


class ModuleDescriptionResource(resources.ModelResource):
    head = fields.Field(column_name='resp',
                        attribute='head',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    head_first_name = fields.Field(column_name='resp_first_name',
                             attribute='head',
                             widget=ForeignKeyWidget(Tutor, 'first_name'))
    head_last_name = fields.Field(column_name='resp_last_name',
                                   attribute='head',
                                   widget=ForeignKeyWidget(Tutor, 'last_name'))
    color_bg = fields.Field(column_name='color_bg',
                                   attribute='display',
                                   widget=ForeignKeyWidget(ModuleDisplay,
                                                           'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                                   attribute='display',
                                   widget=ForeignKeyWidget(ModuleDisplay,
                                                           'color_txt'))
    promo = fields.Field(column_name='promo',
                                   attribute='train_prog',
                                   widget=ForeignKeyWidget(TrainingProgramme,
                                                           'abbrev'))

    class Meta:
        model = Module
        fields = ('name', 'abbrev', 'head', 'resp_first_name', 'resp_last_name',
                  'description', 'color_bg', 'color_txt', 'promo')


class GroupPreferredLinksResource(resources.ModelResource):
    links = fields.Field(column_name='links',
                         attribute='links',
                         widget=ManyToManyWidget('base.Enrichedlink',
                                                 field='concatenated',
                                                 separator='|'))
    group = fields.Field(column_name='group',
                         attribute='group',
                         widget=ForeignKeyWidget('base.Group', 'full_name'))
    class Meta:
        model = GroupPreferredLinks
        fields = ('group', 'links')


# </editor-fold desc="RESOURCES">


# <editor-fold desc="ADMIN_MENU">
# ----------------
# -- ADMIN MENU --
# ----------------

class DepartmentModelAdminMixin():
    #
    # Support filter and udpate of department specific related items
    #
    department_field_name = 'department'
    department_field_tuple = (department_field_name,)

    def get_exclude(self, request, obj=None):
        # Hide department field if a department attribute exists
        # on the related model and a department value has been set
        base = super().get_exclude(request, obj)
        exclude = list() if base is None else list(base)

        if hasattr(request, 'department'):
            for field in self.model._meta.get_fields():
                if (not field.auto_created
                    and field.related_model == Department
                    and not field.name in exclude):
                    exclude.append(field.name)

        return tuple(exclude)

    def save_model(self, request, obj, form, change):
        #
        # Automaticaly associate model to department when required
        #
        m2m_fields = []

        if hasattr(request, 'department'):
            for field in self.model._meta.get_fields():
                if (not change
                        and not field.auto_created
                        and field.related_model == Department):
                    if isinstance(field, related_fields.ForeignKey):
                        setattr(obj, field.name, request.department)
                    elif isinstance(field, related_fields.ManyToManyField):
                        if (field.remote_field.through
                            and field.remote_field.through._meta.auto_created):
                            m2m_fields.append(field)

        super().save_model(request, obj, form, change)

        # Related values need to be set after save model
        for field in m2m_fields:
            getattr(obj, field.name).add(request.department)

    def get_department_lookup(self, department):
        """
	Hook for overriding default department lookup research
	"""
        return get_model_department_lookup(self.model, department)

    def get_queryset(self, request):
        """
	Filter only department related instances
	"""
        qs = super().get_queryset(request)

        try:
            if hasattr(request, 'department'):
                related_filter = self.get_department_lookup(request.department)
                if related_filter:
                    return qs.filter(**related_filter).distinct()
        except FieldDoesNotExist:
            pass

        return qs

    def formfield_with_department_filtering(self, db_field, request, kwargs):
        """
	Filter form fields for with specific department related items
	"""

        if hasattr(request, 'department') and db_field.related_model:
            related_filter = get_model_department_lookup(db_field.related_model,
                                                         request.department)
            if related_filter:
                db = kwargs.get('using')
                queryset = self.get_field_queryset(db, db_field, request)
                if queryset:
                    kwargs["queryset"] = queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        self.formfield_with_department_filtering(db_field, request, kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     self.formfield_with_department_filtering(db_field, request, kwargs)
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_field_queryset(self, db, db_field, request):

        queryset = super().get_field_queryset(db, db_field, request)

        if hasattr(request, 'department'):
            related_filter = get_model_department_lookup(db_field.related_model,
                                                         request.department)

            if related_filter:
                if queryset:
                    return queryset.filter(**related_filter).distinct()
                else:
                    return db_field.remote_field \
                        .model._default_manager \
                        .using(db) \
                        .filter(**related_filter).distinct()

        return queryset


class MyModelAdmin(admin.ModelAdmin):
    save_as = True


class DepartmentModelAdmin(DepartmentModelAdminMixin, MyModelAdmin):
    pass


class HolidayAdmin(MyModelAdmin):
    list_display = ('day', 'week', )
    ordering = ( '-week', 'day')
    list_filter = (
        ('day', DropdownFilterSimple),
        ('week__nb', DropdownFilterAll),
    )


class TrainingHalfDayAdmin(DepartmentModelAdmin):
    list_display = ('train_prog', 'day', 'week', 'apm')
    ordering = ('-week', 'train_prog', 'day')


class StructuralGroupAdmin(DepartmentModelAdmin):
    # list_display = ('name', 'type', 'size', 'train_prog')
    # filter_horizontal = ('parent_groups',)
    # ordering = ('size',)
    # list_filter = (('train_prog', DropdownFilterRel),
    #                )
    pass

class TransversalGroupAdmin(DepartmentModelAdmin):
#     list_display = ('name', 'size', 'train_prog')
#     ordering = ('size',)
#     list_filter = (('train_prog', DropdownFilterRel),
#                    )
    pass
# class RoomInline(admin.TabularInline):
#     model = RoomGroup.subroom_of.through
#     show_change_link = False


class RoomAdmin(DepartmentModelAdmin):
    # inlines = [RoomInline,]
    list_display = ('name',)


class RoomPreferenceAdmin(DepartmentModelAdmin):
    list_display = ('room', 'week', 'day', 'start_time',
                    'duration', 'value')
    ordering = ('-week', 'day', 'start_time')
    list_filter = (
        ('room', DropdownFilterRel),
        ('week__nb', DropdownFilterAll),
    )


class RoomSortAdmin(DepartmentModelAdmin):
    list_display = ('for_type', 'prefer', 'unprefer',)
    list_filter = (
        ('for_type', DropdownFilterRel),
        ('prefer', DropdownFilterRel),
        ('unprefer', DropdownFilterRel),
    )


class ModuleAdmin(DepartmentModelAdmin):
    list_display = ('name', 'ppn', 'abbrev',
                    'head',
                    'train_prog')
    ordering = ('abbrev',)
    list_filter = (
        ('head', DropdownFilterRel),
        ('train_prog', DropdownFilterRel),)


class CourseAdmin(DepartmentModelAdmin):
    list_display = ('module', 'type', 'tutor', 'week')
    ordering = ('week', 'module', 'type', 'no', 'groups', 'tutor')
    list_filter = (
        ('tutor', DropdownFilterRel),
        ('week__nb', DropdownFilterAll),
        ('type', DropdownFilterRel),
        #('groups', DropdownFilterRel),
    )


class CoursPlaceAdmin(DepartmentModelAdmin):

    def course_week(o):
        return str(o.course.week)

    course_week.short_description = _('Week')
    course_week.admin_order_field = 'course__week'

    list_display = (course_week, 'course', 'day', 'start_time',
                    'room')
    ordering = ('-course__week', 'day', 'start_time', 'course', 'room')
    list_filter = (
        ('course__tutor', DropdownFilterRel),
        ('course__week__nb', DropdownFilterAll),
        ('course__week__year', DropdownFilterAll),
    )


class CoursePreferenceAdmin(DepartmentModelAdmin):
    list_display = ('course_type', 'train_prog', 'day', 'start_time',
                    'duration', 'value', 'week')
    ordering = ('-week',)
    list_filter = (('week__nb', DropdownFilterAll),
                   ('train_prog', DropdownFilterRel),
                   )


class DependencyAdmin(DepartmentModelAdmin):
    def course1_week(o):
        return str(o.course1.week)
    
    course1_week.short_description = _('Week')
    course1_week.admin_order_field = 'course1__week'

    ordering = ('-course1__week',)
    list_display = (course1_week, 'course2', 'successive', 'ND', )
    list_filter = (('course1__week__nb', DropdownFilterAll),
                   ('course1__week__year', DropdownFilterAll))


class CourseModificationAdmin(DepartmentModelAdmin):
    def course_week(o):
        return str(o.course.week)

    course_week.short_description = _('Week')
    course_week.admin_order_field = 'course__week'

    list_display = ('course', course_week,
                    'tutor_old',
                    'version_old', 'room_old', 'day_old',
                    'start_time_old', 'updated_at', 'initiator'
                    )
    list_filter = (('initiator', DropdownFilterRel),
                   ('course__week__nb', DropdownFilterAll),
                   ('course__week__year', DropdownFilterAll),)
    ordering = ('-updated_at', '-old_week')


class DispoAdmin(DepartmentModelAdmin):
    list_display = ('user', 'day', 'start_time', 'duration', 'value',
                    'week',)
    ordering = ('user', '-week', 'day', 'start_time', 'value')
    list_filter = (('start_time', DropdownFilterAll),
                   ('week__nb', DropdownFilterAll),
                   ('week__year', DropdownFilterAll),
                   ('user', DropdownFilterRel),
                   )


class RegenAdmin(DepartmentModelAdmin):
    list_display = ('week',
                    'full', 'fdate',
                    'stabilize', 'sdate',)
    ordering = ('-week', )


class EnrichedLinkAdmin(MyModelAdmin):
    list_display = ('url', 'description',)
    ordering = ('description',)


class GroupPreferredLinksAdmin(MyModelAdmin):
    pass

class CourseStartTimeConstraintAdmin(MyModelAdmin):
    pass
# </editor-fold desc="ADMIN_MENU">


# admin.site.unregister(auth.models.User)
admin.site.unregister(auth.models.Group)

admin.site.register(Holiday, HolidayAdmin)
admin.site.register(TrainingHalfDay, TrainingHalfDayAdmin)
admin.site.register(StructuralGroup, StructuralGroupAdmin)
admin.site.register(TransversalGroup, TransversalGroupAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(RoomPreference, RoomPreferenceAdmin)
admin.site.register(RoomSort, RoomSortAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseModification, CourseModificationAdmin)
admin.site.register(CoursePreference, CoursePreferenceAdmin)
admin.site.register(Dependency, DependencyAdmin)
admin.site.register(ScheduledCourse, CoursPlaceAdmin)
admin.site.register(UserPreference, DispoAdmin)
admin.site.register(Regen, RegenAdmin)
admin.site.register(EnrichedLink, EnrichedLinkAdmin)
admin.site.register(GroupPreferredLinks, GroupPreferredLinksAdmin)
admin.site.register(CourseStartTimeConstraint, CourseStartTimeConstraintAdmin)
admin.site.register(Mode, DepartmentModelAdmin)
admin.site.register(CourseType, DepartmentModelAdmin)
admin.site.register(Period, DepartmentModelAdmin)
