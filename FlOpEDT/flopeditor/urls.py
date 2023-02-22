# -*- coding: utf-8 -*-
"""
Python versions: Python 3.6

This file is part of the FlOpEDT/FlOpScheduler project.
Copyright (c) 2017
Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program. If not, see
<http://www.gnu.org/licenses/>.

You can be released from the requirements of the license by purchasing
a commercial license. Buying such a license is mandatory as soon as
you develop activities involving the FlOpEDT/FlOpScheduler software
without disclosing the source code of your own applications.


This module is used to declare the urls related to flop!EDITOR, an app used
to manage a department statistics for FlOpEDT.
"""

from django.urls import path
from . import views, crud

app_name = "flopeditor"

urlpatterns = [
    # directly reachable by users
    # ---------------------------
    path('', views.home, name='flopeditor-home'),
    path('flopeditor-help/', views.flopeditor_help, name='flopeditor-help'),
    path('<slug:department_abbrev>/', views.department_default,
         name='flopeditor-department-default'),
    path('<slug:department_abbrev>/salles', views.department_rooms,
         name='flopeditor-department-rooms'),
    path('<slug:department_abbrev>/intervenants', views.department_tutors,
         name='flopeditor-department-tutors'),
    path('<slug:department_abbrev>/categories-de-salles', views.department_room_types,
         name='flopeditor-department-room-types'),
    path('<slug:department_abbrev>/attributs-de-salles', views.department_room_attributes,
         name='flopeditor-department-room-attributes'),
    path('<slug:department_abbrev>/groupes-structuraux', views.department_student_structural_groups,
         name='flopeditor-department-student-structural-groups'),
    path('<slug:department_abbrev>/groupes-transversaux', views.department_student_transversal_groups,
         name='flopeditor-department-student-transversal-groups'),
    path('<slug:department_abbrev>/natures', views.department_student_group_types,
         name='flopeditor-department-student-group-types'),
    path('<slug:department_abbrev>/promos', views.department_training_programmes,
         name='flopeditor-department-training-programmes'),
    path('<slug:department_abbrev>/etudiants', views.department_students,
         name='flopeditor-department-students'),
    path('<slug:department_abbrev>/modules', views.department_modules,
         name='flopeditor-department-modules'),
    path('<slug:department_abbrev>/types-de-cours', views.department_course_types,
         name='flopeditor-department-course-types'),
    path('<slug:department_abbrev>/semestres', views.department_periods,
         name='flopeditor-department-periods'),

    path('<slug:department_abbrev>/parameters', views.department_parameters,
         name='flopeditor-department-parameters'),
    path('<slug:department_abbrev>/parameters/edit', views.department_parameters_edit,
         name='flopeditor-department-parameters-edit'),
    path('<slug:department_abbrev>/delete', views.department_delete,
         name='flopeditor-department-delete'),



    # exchanges with the db via django
    # --------------------------------
    path('ajax/create-department', views.ajax_create_department,
         name="flopeditor-ajax-create-department"),
    path('ajax/update-department', views.ajax_update_department,
         name="flopeditor-ajax-update-department"),
    path('ajax/parameters-edit/<slug:department_abbrev>', views.ajax_edit_parameters,
         name='flopeditor-ajax-edit-department-parameters'),
    path('ajax/update-profil', views.ajax_update_profil,
         name='flopeditor-ajax-update-profil'),

    # exchanges with the CRUD
    # --------------------------------
    path('<slug:department_abbrev>/crud/rooms', crud.crud_rooms,
         name='flopeditor-crud-rooms'),
    path('<slug:department_abbrev>/crud/tutors', crud.crud_tutors,
         name='flopeditor-crud-tutors'),
    path('<slug:department_abbrev>/crud/room_types', crud.crud_room_types,
         name='flopeditor-crud-room-types'),
    path('<slug:department_abbrev>/crud/room_attributes', crud.crud_room_attributes,
         name='flopeditor-crud-room-attributes'),
    path('<slug:department_abbrev>/crud/group_type', crud.crud_student_group_type,
         name='flopeditor-crud-student-group-type'),
    path('<slug:department_abbrev>/crud/student_structural_group', crud.crud_student_structural_group,
         name='flopeditor-crud-student-structural-group'),
    path('<slug:department_abbrev>/crud/student_transversal_group', crud.crud_student_transversal_group,
         name='flopeditor-crud-student-transversal-group'),
    path('<slug:department_abbrev>/crud/students', crud.crud_students,
         name='flopeditor-crud-students'),
    path('<slug:department_abbrev>/crud/modules', crud.crud_module,
         name='flopeditor-crud-modules'),
    path('<slug:department_abbrev>/crud/training_programmes', crud.crud_training_programmes,
         name='flopeditor-crud-training-programmes'),
    path('<slug:department_abbrev>/crud/courses', crud.crud_course,
         name='flopeditor-crud-courses'),
    path('<slug:department_abbrev>/crud/periods', crud.crud_periods,
         name='flopeditor-crud-periods'),

]
