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

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from django.contrib import admin
import django.contrib.auth as auth

from FlOpEDT.filters import DropdownFilterAll, DropdownFilterRel, \
    DropdownFilterCho
from people.models import Tutor, User
from base.models import Day, RoomGroup, Module, Course, Group, Slot, \
    UserPreference, Time, ScheduledCourse, EdtVersion, CourseModification, \
    PlanningModification, BreakingNews, TrainingProgramme, ModuleDisplay, \
    Regen, Holiday, TrainingHalfDay, RoomPreference, RoomSort, \
    CoursePreference, Dependency, RoomType, CourseType

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
    id = fields.Field(column_name='id_cours',
                      attribute='cours',
                      widget=ForeignKeyWidget(Course, 'id'))
    no = fields.Field(column_name='num_cours',
                      attribute='cours',
                      widget=ForeignKeyWidget(Course, 'no'))
    prof = fields.Field(column_name='prof_nom',
                        attribute='cours__tutor',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    # prof_first_name = fields.Field(column_name='prof_first_name',
    #                                attribute='cours__tutor',
    #                                widget=ForeignKeyWidget(Tutor,
    #                                 'first_name'))
    # prof_last_name = fields.Field(column_name='prof_last_name',
    #                               attribute='cours__tutor',
    #                               widget=ForeignKeyWidget(Tutor, 'last_name'))
    groupe = fields.Field(column_name='gpe_nom',
                          attribute='cours__groupe',
                          widget=ForeignKeyWidget(Group, 'nom'))
    promo = fields.Field(column_name='gpe_promo',
                         attribute='cours__groupe__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    module = fields.Field(column_name='module',
                          attribute='cours__module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    coursetype = fields.Field(column_name='coursetype',
                          attribute='cours__type',
                          widget=ForeignKeyWidget(CourseType, 'name'))
    # day = fields.Field(column_name='day',
    #                     attribute='day',
    #                     widget=ForeignKeyWidget(Day, 'no'))
    # salle = fields.Field(column_name = 'salle',
    #                      attribute = 'salle',
    #                      widget = ForeignKeyWidget(Salle,'nom'))
    room = fields.Field(column_name='room',
                        attribute='room',
                        widget=ForeignKeyWidget(RoomGroup, 'name'))
    room_type = fields.Field(column_name='room_type',
                             attribute='cours__room_type',
                             widget=ForeignKeyWidget(RoomType, 'name'))
    color_bg = fields.Field(column_name='color_bg',
                            attribute='cours__module__display',
                            widget=ForeignKeyWidget(ModuleDisplay, 'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                             attribute='cours__module__display',
                             widget=ForeignKeyWidget(ModuleDisplay, 'color_txt'))

    class Meta:
        model = ScheduledCourse
        fields = ('id', 'no', 'groupe', 'promo', 'color_bg', 'color_txt',
                  'module', 'coursetype', 'day', 'start_time',
                  'semaine', 'room', 'prof', 'room_type')


class CoursResource(resources.ModelResource):
    promo = fields.Field(column_name='promo',
                         attribute='groupe__train_prog',
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
                          attribute='cours__type__duration')
    groupe = fields.Field(column_name='groupe',
                          attribute='groupe',
                          widget=ForeignKeyWidget(Group, 'nom'))
    color_bg = fields.Field(column_name='color_bg',
                            attribute='module__display',
                            widget=ForeignKeyWidget(ModuleDisplay, 'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                             attribute='module__display',
                             widget=ForeignKeyWidget(ModuleDisplay, 'color_txt'))
    room_type = fields.Field(column_name='room_type',
                             attribute='room_type',
                             widget=ForeignKeyWidget(RoomType, 'name'))

    class Meta:
        model = Course
        fields = ('id', 'no', 'tutor_name', 'groupe', 'promo', 'module',
                  'coursetype', 'color_bg', 'color_txt', 'prof', 'room_type')


class SemaineAnResource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ("semaine", "an")


class DispoResource(resources.ModelResource):
    prof = fields.Field(attribute='user',
                        widget=ForeignKeyWidget(User, 'username'))

    class Meta:
        model = UserPreference
        fields = ('day', 'start_time', 'duration', 'valeur', 'prof')


class UnavailableRoomsResource(resources.ModelResource):
    class Meta:
        model = RoomPreference
        fields = ("room", "day", "start_time", "duration")


class BreakingNewsResource(resources.ModelResource):
    class Meta:
        model = BreakingNews
        fields = ("id", "x_beg", "x_end", "y", "txt", "fill_color", "strk_color", "is_linked")

class VersionResource(resources.ModelResource):
    class Meta:
        model = EdtVersion;
        fields = ("an", "semaine", "version")



# </editor-fold desc="RESOURCES">



        
# <editor-fold desc="ADMIN_MENU">
# ----------------
# -- ADMIN MENU --
# ----------------

class BreakingNewsAdmin(admin.ModelAdmin):
    list_display = ('week', 'year', 'x_beg', 'x_end', 'y', 'txt',
                    'fill_color', 'strk_color')
    ordering = ('-year', '-week')


class JourAdmin(admin.ModelAdmin):
    list_display = ('nom', 'no')
    ordering = ('no',)

    
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('day', 'week', 'year')
    ordering = ('-year', '-week', 'day')
    list_filter = (
        ('day', DropdownFilterRel),
        ('year', DropdownFilterAll),
        ('week', DropdownFilterAll),
    )


class TrainingHalfDayAdmin(admin.ModelAdmin):
    list_display = ('train_prog', 'day', 'week', 'year', 'apm')
    ordering = ('-year', '-week', 'train_prog', 'day')
    

# class DemiJourAdmin(admin.ModelAdmin):
#    list_display = ('jour','apm')
#    ordering = ('jour','apm')


# # from django.utils.text import Truncator
# ordering = ('abbrev',)
#    def abb_name(self,prof):
#        return Truncator(prof.nom).chars(4, truncate='.')
#    abb_name.short_description = 'Aperçu du nom'


class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'size', 'train_prog')
    filter_horizontal = ('parent_groups',)
    ordering = ('size',)
    list_filter = (('train_prog', DropdownFilterRel),
                   )


# class SalleAdmin(admin.ModelAdmin):
#     list_display = ('nom','tp_ok','td_ok','ce_ok','machine','exam')

class RoomGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)

    
class RoomPreferenceAdmin(admin.ModelAdmin):
    list_display = ('room', 'semaine', 'an', 'day', 'start_time',
                    'duration', 'valeur')
    ordering = ('-an','-semaine', 'day', 'start_time')
    list_filter = (
        ('room', DropdownFilterRel),
        ('an', DropdownFilterAll),
        ('semaine', DropdownFilterAll),
    )

    
class RoomSortAdmin(admin.ModelAdmin):
    list_display = ('for_type', 'prefer', 'unprefer',)
    list_filter = (
        ('for_type', DropdownFilterRel),
        ('prefer', DropdownFilterRel),
        ('unprefer', DropdownFilterRel),
    )

    
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ppn', 'abbrev',
                    'head',
                    'train_prog')
    ordering = ('abbrev',)
    list_filter = (
        ('head', DropdownFilterRel),
        ('train_prog', DropdownFilterRel),)


class CoursAdmin(admin.ModelAdmin):
    list_display = ('module', 'type', 'groupe', 'tutor', 'semaine', 'an')
    ordering = ('an', 'semaine', 'module', 'type', 'no', 'groupe', 'tutor')
    list_filter = (
        ('tutor', DropdownFilterRel),
        ('an', DropdownFilterAll),
        ('semaine', DropdownFilterAll),
        ('type', DropdownFilterRel),
        ('groupe', DropdownFilterRel),
    )


class CoursPlaceAdmin(admin.ModelAdmin):

    def cours_semaine(o):
        return str(o.cours.semaine)

    cours_semaine.short_description = 'Semaine'
    cours_semaine.admin_order_field = 'cours__semaine'

    def cours_an(o):
        return str(o.cours.an)

    cours_an.short_description = 'Année'
    cours_an.admin_order_field = 'cours__an'

    list_display = (cours_semaine, cours_an, 'cours', 'day', 'start_time', 'room')
    ordering = ('day', 'start_time', 'cours', 'room')
    list_filter = (
        ('cours__tutor', DropdownFilterRel),
        ('cours__an', DropdownFilterAll),
        ('cours__semaine', DropdownFilterAll),)


class EdtVAdmin(admin.ModelAdmin):
    list_display = ('semaine', 'version', 'an')
    ordering = ('-an', '-semaine', 'version')
    list_filter = (('semaine', DropdownFilterAll),
                   ('an', DropdownFilterAll)
                   )


class CoursePreferenceAdmin(admin.ModelAdmin):
    list_display = ('course_type', 'train_prog', 'day', 'start_time',
                    'duration', 'valeur', 'semaine', 'an')
    ordering = ('-an', '-semaine')
    list_filter = (('semaine', DropdownFilterAll),
                   ('an', DropdownFilterAll),
                   ('train_prog', DropdownFilterRel),
                   )
    

class DependencyAdmin(admin.ModelAdmin):
    def cours1_semaine(o):
        return str(o.cours.semaine)

    cours1_semaine.short_description = 'Semaine'
    cours1_semaine.admin_order_field = 'cours1__semaine'

    def cours1_an(o):
        return str(o.cours.an)

    cours1_an.short_description = 'Année'
    cours1_an.admin_order_field = 'cours1__an'

    list_display = ('cours1', 'cours2', 'successifs', 'ND')
    list_filter = (('cours1__an', DropdownFilterAll),
                   ('cours1__semaine', DropdownFilterAll),
                   )

    
class CoursMAdmin(admin.ModelAdmin):
    def cours_semaine(o):
        return str(o.cours.semaine)

    cours_semaine.short_description = 'Semaine'
    cours_semaine.admin_order_field = 'cours__semaine'

    def cours_an(o):
        return str(o.cours.an)

    cours_an.short_description = 'Année'
    cours_an.admin_order_field = 'cours__an'

    list_display = ('cours', cours_semaine, cours_an,
                    'version_old', 'room_old', 'day_old',
                    'start_time_old', 'updated_at', 'initiator'
                    )
    list_filter = (('initiator', DropdownFilterRel),
                   ('cours__an', DropdownFilterAll),
                   ('cours__semaine', DropdownFilterAll),)
    ordering = ('-updated_at', 'an_old', 'semaine_old')


class PlanifMAdmin(admin.ModelAdmin):
    list_display = ('cours', 'semaine_old', 'an_old',
                    'tutor_old',
                    'updated_at',
                    'initiator'
                    )
    ordering = ('-updated_at', 'an_old', 'semaine_old')
    list_filter = (('initiator', DropdownFilterRel),
                   ('semaine_old', DropdownFilterAll),
                   ('an_old', DropdownFilterAll),)


class DispoAdmin(admin.ModelAdmin):
    list_display = ('user', 'day', 'start_time', 'duration', 'valeur',
                    'semaine', 'an')
    ordering = ('user', 'an', 'semaine', 'day', 'start_time', 'valeur')
    list_filter = (('start_time', DropdownFilterAll),
                   ('semaine', DropdownFilterAll),
                   ('user', DropdownFilterRel),
                   )



class RegenAdmin(admin.ModelAdmin):
    list_display = ('an', 'semaine', 'full', 'fday', 'fmonth', 'fyear', 'stabilize', 'sday', 'smonth', 'syear', )
    ordering = ('-an', '-semaine')






# </editor-fold desc="ADMIN_MENU">




# admin.site.unregister(auth.models.User)
admin.site.unregister(auth.models.Group)

# admin.site.register(Jour, JourAdmin)
# admin.site.register(DemiJour, DemiJourAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(TrainingHalfDay, TrainingHalfDayAdmin)
admin.site.register(Group, GroupeAdmin)
admin.site.register(RoomGroup, RoomGroupAdmin)
admin.site.register(RoomPreference, RoomPreferenceAdmin)
admin.site.register(RoomSort, RoomSortAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Course, CoursAdmin)
admin.site.register(EdtVersion, EdtVAdmin)
admin.site.register(CourseModification, CoursMAdmin)
admin.site.register(CoursePreference, CoursePreferenceAdmin)
admin.site.register(Dependency, DependencyAdmin)
admin.site.register(PlanningModification, PlanifMAdmin)
admin.site.register(ScheduledCourse, CoursPlaceAdmin)
# admin.site.register(CoursLP, CoursLPAdmin)
admin.site.register(UserPreference, DispoAdmin)
admin.site.register(BreakingNews, BreakingNewsAdmin)
admin.site.register(Regen,RegenAdmin)
