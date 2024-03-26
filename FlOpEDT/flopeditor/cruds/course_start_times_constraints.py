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

import datetime as dt

from django.http import JsonResponse

from base.models import (
    CourseStartTimeConstraint,
    CourseType,
    GroupType,
    TimeGeneralSettings,
)
from base.timing import min_to_str, str_to_min
from flopeditor.validator import ERROR_RESPONSE, OK_RESPONSE, validate_course_values


def possible_start_time(department):
    """
    Return all possibles start time
    :param department: Department.
    :type department:  base.models.Department
    :return: list of minutes
    :rtype:  list(int)

    """
    time = TimeGeneralSettings.objects.get(department=department)
    horaire = dt.datetime.combine(dt.date(1, 1, 1), time.day_start_time)
    possible_start_time_list = []
    while horaire.time() <= time.day_end_time:
        possible_start_time_list.append(horaire.time().strftime("%H:%M"))
        horaire += dt.timedelta(minutes=5)
    return possible_start_time_list


def get_start_time(new_starts_times):
    """
    Return all start time in minute
    :param department: list of string (ex:"8:30").
    :type department:  list of string
    :return: list of start time in minute
    :rtype:  list(int)

    """
    start_time_list = []
    for start_time_str in new_starts_times:
        start_time_list.append(dt.datetime.strptime(start_time_str, "%H:%M").time())
    start_time_list.sort()
    return start_time_list


def read(department):
    """Return all course type for a department
    :param department: Department.q
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """

    course_start_time_constraints = CourseStartTimeConstraint.objects.filter(
        department=department
    )

    values = []
    for cstc in course_start_time_constraints:
        list_starts_times = []
        for value in cstc.allowed_start_times:
            list_starts_times.append(value.strftime("%H:%M"))

        values.append((cstc.duration.seconds // 60, list_starts_times))

    return JsonResponse(
        {
            "columns": [
                {"name": "Durée (en min)", "type": "int", "options": {}},
                {
                    "name": "Horaire auxquels ce type de cours peut commencer",
                    "type": "select-chips",
                    "options": {"values": possible_start_time(department)},
                },
            ],
            "values": values,
            "options": {
                "examples": [
                    [90, ["08:00", "09:30", "11:00", "14:15", "15:45"]],
                    [120, ["10:00", "14:15", "16:15"]],
                    [240, ["08:00", "14:15"]],
                ]
            },
        }
    )


def create(entries, department):
    """Create values for course type
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries["result"] = []
    for i in range(len(entries["new_values"])):
        new_duration_minutes = entries["new_values"][i][0]
        new_duration = dt.timedelta(minutes=new_duration_minutes)
        new_starts_times = entries["new_values"][i][1]

        if CourseStartTimeConstraint.objects.filter(
            duration=new_duration, department=department
        ):
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Un contrainte avec cette durée est déjà présent dans la base de données.",
                ]
            )
            return entries

        new_cstc = CourseStartTimeConstraint.objects.create(
            department=department,
            duration=new_duration,
            allowed_start_times=get_start_time(new_starts_times),
        )

        entries["result"].append([OK_RESPONSE])

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

    entries["result"] = []
    if len(entries["old_values"]) != len(entries["new_values"]):
        return entries

    for i in range(len(entries["old_values"])):
        old_duration_minutes = entries["old_values"][i][0]
        old_duration = dt.timedelta(minutes=old_duration_minutes)
        new_duration_minutes = entries["new_values"][i][0]
        new_duration = dt.timedelta(minutes=new_duration_minutes)
        new_starts_times = entries["new_values"][i][1]

        try:
            cstc_to_update = CourseStartTimeConstraint.objects.get(
                duration=old_duration, department=department
            )

            if (
                CourseStartTimeConstraint.objects.filter(
                    duration=new_duration, department=department
                ).exists()
                and old_duration != new_duration
            ):
                entries["result"].append(
                    [
                        ERROR_RESPONSE,
                        "Lex contraintes pour cette durée sont déjà définie.",
                    ]
                )
            else:
                cstc_to_update.duration = new_duration

                cstc_to_update.allowed_start_times = get_start_time(new_starts_times)

                cstc_to_update.save()
                entries["result"].append([OK_RESPONSE])
        except CourseStartTimeConstraint.DoesNotExist:
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Un durée à modifier n'a pas été trouvée dans la base de données.",
                ]
            )
        except CourseStartTimeConstraint.MultipleObjectsReturned:
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Plusieurs contraintes avec la même durée existent en base de données.",
                ]
            )

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

    entries["result"] = []
    for i in range(len(entries["old_values"])):
        old_duration_minutes = entries["old_values"][i][0]
        old_duration = dt.timedelta(minutes=old_duration_minutes)

        try:
            CourseStartTimeConstraint.objects.get(
                department=department, duration=old_duration
            ).delete()
            entries["result"].append([OK_RESPONSE])
        except CourseStartTimeConstraint.DoesNotExist:
            entries["result"].append([ERROR_RESPONSE, "Erreur en base de données."])
    return entries
