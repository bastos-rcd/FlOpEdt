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

"""

from django.http import JsonResponse

from base.models import (CourseType, GroupType)
from flopeditor.validator import (ERROR_RESPONSE, OK_RESPONSE,
                                  validate_course_values)


def groups_types(department):
    """
    Return all name of group type for department
    :return: list of  name of group type
    :rtype:  list(strng)

    """
    group_types = GroupType.objects.filter(department=department)
    groups_types_list = []
    for group in group_types:
        groups_types_list.append(group.name)
    return groups_types_list



def read(department):
    """Return all course type for a department
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """

    course_types = CourseType.objects.filter(department=department)

    values = []
    for ctype in course_types:
        ctype_list_group = []

        for group_type in ctype.group_types.all():
            ctype_list_group.append(group_type.name)

        if ctype.graded:
            graded = "Oui"
        else:
            graded = "Non"

        values.append((ctype.name,
                       ctype_list_group,
                       graded))

    return JsonResponse({
        "columns":  [{
            'name': 'Type de cours',
            "type": "text",
            "options": {}
        }, {
            'name': 'Types de groupes concernés',
            "type": "select-chips",
            "options": {"values": groups_types(department)}
        }, {
            'name': 'Evalué', 
            "type": "select",
            "options": {"values" : ["Non", "Oui"]}
         }
        ],
        "values": values,
        "options": {
            "examples": [
                ["Amphi", ["C"], "Non"],
                ["Exam", ["C"], "Oui"],
                ["TP120", ["TPA", "TPB"], "Non"]
            ]
        }
    })


def create(entries, department):
    """Create values for course type
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    for i in range(len(entries['new_values'])):
        new_course_type = entries['new_values'][i][0]
        new_types_groups = entries['new_values'][i][1]
        is_graded_str = entries['new_values'][i][2]
        if is_graded_str == "Oui":
            is_graded = True
        else:
            is_graded = False

        if not validate_course_values(new_course_type, entries):
            return entries

        if CourseType.objects.filter(name=new_course_type, department=department):
            entries['result'].append([
                ERROR_RESPONSE,
                "Un type de cours avec ce nom est déjà présent dans la base de données."
            ])
            return entries

        new_course = CourseType.objects.create(name=new_course_type,
                                               department=department,
                                               graded=is_graded)
        for name in new_types_groups:
            new_course.group_types.add(GroupType.objects.get(
                name=name, department=department))
        new_course.save()

        entries['result'].append([OK_RESPONSE])

    return entries


def update(entries, department):
    """Update values for course type
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

    for i in range(len(entries['old_values'])):
        old_course_type = entries['old_values'][i][0]
        new_course_type = entries['new_values'][i][0]
        new_types_groups = entries['new_values'][i][1]
        is_graded_str = entries['new_values'][i][2]
        if is_graded_str == "Oui":
            new_is_graded = True
        else:
            new_is_graded = False

        if not validate_course_values(new_course_type, entries):
            return entries

        try:
            course_type_to_update = CourseType.objects.get(name=old_course_type,
                                                           department=department)

            if CourseType.objects.filter(name=new_course_type, department=department)\
                    and old_course_type != new_course_type:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Le nom de ce type de cours est déjà utilisée."])
            else:
                course_type_to_update.name = new_course_type
                course_type_to_update.graded = new_is_graded
                course_type_to_update.group_types.remove(
                    *course_type_to_update.group_types.all())
                for name in new_types_groups:
                    course_type_to_update.group_types.add(
                        GroupType.objects.get(name=name, department=department))
                course_type_to_update.save()
                entries['result'].append([OK_RESPONSE])
        except CourseType.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Un type de cours à modifier n'a pas été trouvée dans la base de données."])
        except CourseType.MultipleObjectsReturned:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Plusieurs type de cours du même nom existent en base de données."])

    return entries


def delete(entries, department):
    """Delete values for rooms
    :param entries: Values to delete.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    for i in range(len(entries['old_values'])):
        old_course_type = entries['old_values'][i][0]
        try:
            CourseType.objects.get(name=old_course_type,
                                   department=department).delete()
            entries['result'].append([OK_RESPONSE])
        except CourseType.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Erreur en base de données."])
    return entries
