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

This module is used to create, read, update and/or delete a group type
(TP, TD,...) related to a department
"""

from django.http import JsonResponse
from base.models import StructuralGroup, TrainingProgramme, GroupType, TransversalGroup, GenericGroup
from flopeditor.validator import OK_RESPONSE, ERROR_RESPONSE, \
    validate_student_values, student_groups_from_full_names
from people.models import Student, User, UserDepartmentSettings


def read(department):
    """Return all student of the department

    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    training_programmes = TrainingProgramme.objects.filter(department=department)
    generic_groups = GenericGroup.objects.filter(train_prog__in=training_programmes)
    students = Student.objects.filter(generic_groups__in=generic_groups)

    values = []
    generic_group_choices = [gg.full_name for gg in generic_groups]
    for student in students:
        groups_list = [g.full_name for g in student.generic_groups.all()]

        values.append((student.username,
                       student.first_name,
                       student.last_name,
                       student.email,
                       groups_list))
		
    return JsonResponse({
        "columns":  [{
            'name': 'Login',
            "type": "text",
            "options": {}
        }, {
            'name': 'Prénom',
            "type": "text",
            "options": {}
        }, {
            'name': 'Nom',
            "type": "text",
            "options": {}
        }, {
            'name': 'Email',
            "type": "text",
            "options": {}
        }, {
            'name': 'Groupes',
            "type": "select-chips",
            "options": {
                "values": generic_group_choices
            }
        }],
        "values": values,
        "options": {
        }
    })


def create(entries, department):
    """Create values for group type in the department
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []

    for i in range(len(entries['new_values'])):
        if not validate_student_values(entries['new_values'][i], entries):
            pass
        else:
            if User.objects.filter(username=entries['new_values'][i][0]).exists():
                entries['result'].append([
                    ERROR_RESPONSE,
                    "username déjà utilisé par quelqu'un·e d'autre."
                ])
            else:
                student = Student.objects.create(
                    username=entries['new_values'][i][0],
                    first_name=entries['new_values'][i][1],
                    last_name=entries['new_values'][i][2],
                    email=entries['new_values'][i][3])
                gp_to_be_set = student_groups_from_full_names(entries['new_values'][i][4], department)
                student.generic_groups.set(gp_to_be_set)
                student.is_student = True
                student.save()
                UserDepartmentSettings(user=student, department=department).save()

    return entries


def update(entries, department):
    """Update values for group type in the department
    :param entries: Values to modify.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """
    entries['result'] = []
    if len(entries['old_values']) != len(entries['new_values']):
        return entries

    entries['result'] = []
    for i in range(len(entries['old_values'])):
        if not validate_student_values(entries['new_values'][i], entries):
            pass
        elif User.objects.filter(username=entries['new_values'][i][0]) and \
                entries['old_values'][i][0] != entries['new_values'][i][0]:
            entries['result'].append([
                ERROR_RESPONSE,
                "Login déjà utilisé par quelqu'un·e d'autre."
            ])
        else:
            try:
                student_to_update = Student.objects.get(
                    username=entries['old_values'][i][0])
                student_to_update.username = entries['new_values'][i][0]
                student_to_update.first_name = entries['new_values'][i][1]
                student_to_update.last_name = entries['new_values'][i][2]
                student_to_update.email = entries['new_values'][i][3]
                new_groups = student_groups_from_full_names(entries['new_values'][i][4], department)
                student_to_update.generic_groups.set(new_groups)
                student_to_update.save()

                entries['result'].append([OK_RESPONSE])
            except Student.DoesNotExist:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Un⋅e étudiant⋅e à modifier n'a pas été trouvé⋅e dans la base de données."])
    return entries


def delete(entries, department):
    """Delete values for group type in the department
    :param entries: Values to delete.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    for i in range(len(entries['old_values'])):
        username = entries['old_values'][i][0]
        try:
            student = Student.objects.get(username=username)
            student.delete()
            entries['result'].append([OK_RESPONSE])

        except Student.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Un⋅e étudiant⋅e à supprimer n'a pas été trouvé⋅e dans la base de données."])
    return entries
