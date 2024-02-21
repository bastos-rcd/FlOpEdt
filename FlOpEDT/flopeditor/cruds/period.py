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
from base.models import TrainingPeriod
from flopeditor.validator import OK_RESPONSE, ERROR_RESPONSE, validate_period_values


def read(department):
    """Return all periods for a department
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """

    periods = TrainingPeriod.objects.filter(department=department)

    values = []
    for period in periods:
        values.append((period.name, period.starting_week, period.ending_week))
    return JsonResponse({
        "columns":  [{
            'name': 'Id du semestre',
            "type": "text",
            "options": {}
        }, {
            'name': 'Semaine de début',
            "type": "int",
            "options": {}
        }, {
            'name': 'Semaine de fin',
            "type": "int",
            "options": {}
        }],
        "values": values,
        "options": {
            "examples": [
                ["S1", 36, 5]
            ]
        }
    })

def create(entries, department):
    """Create values for period
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    for i in range(len(entries['new_values'])):
        new_name = entries['new_values'][i][0]
        new_starting_week = entries['new_values'][i][1]
        new_ending_week = entries['new_values'][i][2]
        if not validate_period_values(new_name, new_starting_week, new_ending_week, entries):
            pass
        elif TrainingPeriod.objects.filter(name=new_name, department=department):
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Le semestre à ajouter est déjà présent dans la base de données.",
                ]
            )
        else:
            TrainingPeriod.objects.create(
                name=new_name,
                department=department,
                starting_week=new_starting_week,
                ending_week=new_ending_week,
            )
            entries["result"].append([OK_RESPONSE])
    return entries





def update(entries, department):
    """Update values for period
    :param entries: Values to modify.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    if len(entries['old_values']) != len(entries['new_values']):
        # old and new values must have same size
        return entries
    for i in range(len(entries['old_values'])):
        old_name = entries['old_values'][i][0]
        new_name = entries['new_values'][i][0]
        new_starting_week = entries['new_values'][i][1]
        new_ending_week = entries['new_values'][i][2]
        if not validate_period_values(new_name, new_starting_week, new_ending_week, entries):
            pass

        else:
            try:
                period_to_update = TrainingPeriod.objects.get(
                    name=old_name, department=department
                )
                if old_name != new_name and TrainingPeriod.objects.filter(
                    name=new_name, department=department
                ):
                    entries["result"].append(
                        [ERROR_RESPONSE, "Le nom du semestre est déjà utilisé."]
                    )
                else:
                    period_to_update.name = new_name
                    period_to_update.starting_week = new_starting_week
                    period_to_update.ending_week = new_ending_week
                    period_to_update.save()
                    entries["result"].append([OK_RESPONSE])
            except TrainingPeriod.DoesNotExist:
                entries["result"].append(
                    [
                        ERROR_RESPONSE,
                        "Un semestre à modifier n'a pas été trouvé dans la base de données.",
                    ]
                )
            except TrainingPeriod.MultipleObjectsReturned:
                entries["result"].append(
                    [
                        ERROR_RESPONSE,
                        "Plusieurs semestres du même nom existent en base de données.",
                    ]
                )

    return entries


def delete(entries, department):
    """Delete values for period
    :param entries: Values to delete.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """
    entries["result"] = []
    for i in range(len(entries["old_values"])):
        old_name = entries["old_values"][i][0]
        try:
            TrainingPeriod.objects.get(name=old_name, department=department).delete()
            entries["result"].append([OK_RESPONSE])
        except TrainingPeriod.DoesNotExist:
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Un semestre à supprimer n'a pas été trouvé dans la base de données.",
                ]
            )
    return entries
