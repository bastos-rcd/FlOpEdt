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
from base.models import CourseType, CourseStartTimeConstraint, GroupType, TimeGeneralSettings
from base.timing import min_to_str, str_to_min
from flopeditor.validator import validate_course_values, OK_RESPONSE, ERROR_RESPONSE


def possible_start_time(department):
    """
    Return all possibles start time
    :param department: Department.
    :type department:  base.models.Department
    :return: list of minutes
    :rtype:  list(int)

    """
    time = TimeGeneralSettings.objects.get(department=department)
    horaire = time.day_start_time
    possible_start_time_list = []
    while horaire <= time.day_finish_time:
        possible_start_time_list.append(min_to_str(horaire))
        horaire += 5
    return possible_start_time_list


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


def get_start_time(new_starts_times):
    """
    Return all start time in minute
    :param department: list of string (ex:"8:30").
    :type department:  list of string
    :return: list of start time in minute
    :rtype:  list(int)

    """
    start_time_list = []
    for start_time in new_starts_times:
        start_time_list.append(str_to_min(start_time))
    return start_time_list


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

        starts_times = CourseStartTimeConstraint.objects.get(
            course_type=ctype)

        list_starts_times = []
        for value_in_minute in starts_times.allowed_start_times:
            list_starts_times.append(min_to_str(value_in_minute))
        
        if ctype.graded:
            graded = "Oui"
        else:
            graded = "Non"

        values.append((ctype.name, ctype.duration,
                       ctype_list_group, list_starts_times,
                       graded))

    return JsonResponse({
        "columns":  [{
            'name': 'Type de cours',
            "type": "text",
            "options": {}
        }, {
            'name': 'Durée (en min)',
            "type": "int",
            "options": {}
        }, {
            'name': 'Types de groupes concernés',
            "type": "select-chips",
            "options": {"values": groups_types(department)}
        }, {
            'name': 'Horaire auxquels ce type de cours peut commencer',
            "type": "select-chips",
            "options": {"values": possible_start_time(department)}
        }, {
            'name': 'Evalué', 
            "type": "select",
            "options": {"values" : ["Non", "Non"]}
         }
        ],
        "values": values,
        "options": {
            "examples": [
                ["Amphi", 90, ["C"], ["08:00", "09:30", "11:00", "14:15", "15:45"], "Non"],
                ["Exam", 120, ["C"], ["08:00", "14:15"], "Oui"],
                ["TP120", 120, ["TPA", "TPB"], ["10:00", "14:15", "16:15"], "Non"]
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
        new_duration = entries['new_values'][i][1]
        new_types_groups = entries['new_values'][i][2]
        new_starts_ti = entries['new_values'][i][3]
        is_graded_str = entries['new_values'][i][4]
        if is_graded_str == "Oui":
            is_graded = True
        else:
            is_graded = False

        if not validate_course_values(new_course_type, new_duration, entries):
            return entries

        if CourseType.objects.filter(name=new_course_type, department=department):
            entries['result'].append([
                ERROR_RESPONSE,
                "Un type de cours avec ce nom est déjà présent dans la base de données."
            ])
            return entries

        new_course = CourseType.objects.create(name=new_course_type,
                                               department=department,
                                               duration=new_duration,
                                               graded=is_graded)
        for name in new_types_groups:
            new_course.group_types.add(GroupType.objects.get(
                name=name, department=department))
        new_course.save()
        CourseStartTimeConstraint.objects.create(course_type=new_course,
                                                 allowed_start_times=get_start_time(new_starts_ti))

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
        new_duration = entries['new_values'][i][1]
        new_types_groups = entries['new_values'][i][2]
        new_starts_times = entries['new_values'][i][3]
        is_graded_str = entries['new_values'][i][4]
        if is_graded_str == "Oui":
            new_is_graded = True
        else:
            new_is_graded = False

        if not validate_course_values(new_course_type, new_duration, entries):
            return entries

        try:
            course_type_to_update = CourseType.objects.get(name=old_course_type,
                                                           department=department)
            course_start_time = CourseStartTimeConstraint.objects.get(
                course_type=course_type_to_update)
            if CourseType.objects.filter(name=new_course_type, department=department)\
                    and old_course_type != new_course_type:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Le nom de ce type de cours est déjà utilisée."])
            else:
                course_type_to_update.name = new_course_type
                course_type_to_update.duration = new_duration
                course_type_to_update.graded = new_is_graded
                course_type_to_update.group_types.remove(
                    *course_type_to_update.group_types.all())
                for name in new_types_groups:
                    course_type_to_update.group_types.add(
                        GroupType.objects.get(name=name, department=department))

                course_start_time.allowed_start_times = get_start_time(
                    new_starts_times)

                course_start_time.save()
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
        old_duration = entries['old_values'][i][1]

        try:
            CourseType.objects.get(name=old_course_type,
                                   department=department,
                                   duration=old_duration).delete()
            entries['result'].append([OK_RESPONSE])
        except CourseType.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Erreur en base de données."])
    return entries
