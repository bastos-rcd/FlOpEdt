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

from base.models import GroupType
from flopeditor.validator import ERROR_RESPONSE, OK_RESPONSE


def read(department):
    """Return all groups types in the department

    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    groups_types = GroupType.objects.filter(department=department)
    values = []
    for group_type in groups_types:
        values.append((group_type.name,))
    return JsonResponse(
        {
            "columns": [{"name": "Id", "type": "text", "options": {}}],
            "values": values,
            "options": {
                "examples": [
                    ["TP"],
                    ["TD"],
                    ["CE (Classe Entière)"],
                    ["TD Alt (TD Alternance)"],
                    ["TP Alt (TP Alternance)"],
                ]
            },
        }
    )


def create(entries, department):
    """Create values for group type in the department
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries["result"] = []
    for i in range(len(entries["new_values"])):
        new_name = entries["new_values"][i][0]
        # verifier la longueur du nom
        if len(new_name) > 50:
            entries["result"].append(
                [ERROR_RESPONSE, "Le nom du type de goupe est trop long."]
            )
        elif not new_name:
            entries["result"].append(
                [ERROR_RESPONSE, "Le nom du type de goupe ne peut pas être vide."]
            )
        else:
            if GroupType.objects.filter(name=new_name, department=department):
                entries["result"].append(
                    [
                        ERROR_RESPONSE,
                        "Le type de goupe est déjà présent dans le département.",
                    ]
                )
            else:
                group_type = GroupType.objects.create(name=new_name)
                group_type.department = department
                group_type.save()
                entries["result"].append([OK_RESPONSE])
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

    if len(entries["old_values"]) != len(entries["new_values"]):
        # old and new values must have same size
        return entries
    entries["result"] = []
    for i in range(len(entries["old_values"])):
        old_name = entries["old_values"][i][0]
        new_name = entries["new_values"][i][0]
        if len(new_name) > 50:
            entries["result"].append(
                [ERROR_RESPONSE, "Le nom du type de goupe est trop long."]
            )
        elif not new_name:
            entries["result"].append(
                [ERROR_RESPONSE, "Le nom du type de goupe ne peut pas être vide."]
            )

        elif (
            GroupType.objects.filter(name=new_name, department=department).count() != 0
        ):
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Un nom de groupe est déjà utilisé dans le département.",
                ]
            )
        else:
            try:
                group_type_to_update = GroupType.objects.get(
                    name=old_name, department=department
                )
                group_type_to_update.name = new_name
                group_type_to_update.save()
                entries["result"].append([OK_RESPONSE])
            except GroupType.DoesNotExist:
                entries["result"].append(
                    [
                        ERROR_RESPONSE,
                        "Un type de goupe à modifier n'a pas été trouvé dans le département.",
                    ]
                )
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

    entries["result"] = []
    for i in range(len(entries["old_values"])):
        old_name = entries["old_values"][i][0]
        try:
            GroupType.objects.get(name=old_name, department=department).delete()
            entries["result"].append([OK_RESPONSE])
        except GroupType.DoesNotExist:
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Un type de goupe à supprimer n'a pas été trouvé dans le département.",
                ]
            )
    return entries
