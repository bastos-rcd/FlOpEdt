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

"""

from django.http import JsonResponse

from base.models import TrainingProgramme
from flopeditor.validator import (
    ERROR_RESPONSE,
    OK_RESPONSE,
    validate_training_programme_values,
)


def read(department):
    """Return all rooms for a department
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    training_programmes = TrainingProgramme.objects.filter(department=department)
    values = []
    for programme in training_programmes:
        values.append((programme.abbrev, programme.name))
    return JsonResponse(
        {
            "columns": [
                {"name": "Abbréviation de vos promos", "type": "text", "options": {}},
                {"name": "Nom de vos promos", "type": "text", "options": {}},
            ],
            "values": values,
            "options": {
                "examples": [
                    ["INFO1", "DUT Informatique première année"],
                    ["INFO2", "DUT Informatique deuxième année"],
                ]
            },
        }
    )


def create(entries, department):
    """Create values for training programmes
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries["result"] = []
    for i in range(len(entries["new_values"])):
        new_abbrev = entries["new_values"][i][0]
        new_name = entries["new_values"][i][1]
        if not validate_training_programme_values(new_abbrev, new_name, entries):
            pass
        elif TrainingProgramme.objects.filter(abbrev=new_abbrev, department=department):
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "La promo à ajouter est déjà présente dans la base de données.",
                ]
            )
        else:
            TrainingProgramme.objects.create(
                name=new_name, abbrev=new_abbrev, department=department
            )
            entries["result"].append([OK_RESPONSE])
    return entries


def update(entries, department):
    """Update values for rooms
    :param entries: Values to modify.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries["result"] = []
    if len(entries["old_values"]) != len(entries["new_values"]):
        # old and new values must have same size
        return entries
    for i in range(len(entries["old_values"])):
        old_abbrev = entries["old_values"][i][0]
        old_name = entries["old_values"][i][1]
        new_abbrev = entries["new_values"][i][0]
        new_name = entries["new_values"][i][1]

        if validate_training_programme_values(new_abbrev, new_name, entries):
            try:
                programme_to_update = TrainingProgramme.objects.get(
                    abbrev=old_abbrev, name=old_name, department=department
                )
                if old_abbrev != new_abbrev and TrainingProgramme.objects.filter(
                    abbrev=new_abbrev, department=department
                ):
                    entries["result"].append(
                        [
                            ERROR_RESPONSE,
                            "L'abbréviation de cette promo est déjà utilisée.",
                        ]
                    )
                else:
                    programme_to_update.abbrev = new_abbrev
                    programme_to_update.name = new_name
                    programme_to_update.save()
                    entries["result"].append([OK_RESPONSE])
            except TrainingProgramme.DoesNotExist:
                entries["result"].append(
                    [
                        ERROR_RESPONSE,
                        "Une promo à modifier n'a pas été trouvée dans la base de données.",
                    ]
                )
            except TrainingProgramme.MultipleObjectsReturned:
                entries["result"].append(
                    [
                        ERROR_RESPONSE,
                        "Plusieurs promos du même nom existent en base de données.",
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
        old_abbrev = entries["old_values"][i][0]
        old_name = entries["old_values"][i][1]
        try:
            TrainingProgramme.objects.get(
                abbrev=old_abbrev, name=old_name, department=department
            ).delete()
            entries["result"].append([OK_RESPONSE])
        except TrainingProgramme.DoesNotExist:
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Une promo à supprimer n'a pas été trouvée dans la base de données.",
                ]
            )
    return entries
