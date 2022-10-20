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
from base.models import RoomAttribute, BooleanRoomAttribute, NumericRoomAttribute
from flopeditor.validator import validate_room_attributes_values, OK_RESPONSE, ERROR_RESPONSE


def read(department):
    """Return all room attributes
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    attributes = RoomAttribute.objects.all()
    values = []
    for attribute in attributes:
        if attribute.is_boolean():
            values.append((attribute.name, attribute.description, "Booléen"))
        else:
            values.append((attribute.name, attribute.description, "Numérique"))
    return JsonResponse({
        "columns" :  [{
            'name': "Nom de l'attribut",
            "type": "text",
            "options": {}
        }, {
            'name': 'Description',
            "type": "text",
            "options": {}
        },
            {
                'name': "Type de l'attribut",
                "type": "select",
                "options": {
                    "values": ["Booléen", "Numérique"]
                }
            }
        ],
        "values" : values,
        "options": {
            "examples": [
                ("Vidéoproj", "Doté d'un vidéoprojecteur", "Boolean"),
                ("Places", "Nombre de places assises", "Numeric")
            ]
        }
        })


def create(entries, department):
    """Create values for room attributes
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
        new_description = entries['new_values'][i][1]
        new_attribute_type = entries['new_values'][i][2]
        if not validate_room_attributes_values(new_name, new_description, entries):
            pass
        elif RoomAttribute.objects.filter(name=new_name).exists():
            entries['result'].append([
                ERROR_RESPONSE,
                "Un attribut portant ce nom est déjà présent dans la base de données."
            ])
        else:
            if new_attribute_type == "Booléen":
                BooleanRoomAttribute.objects.create(name=new_name,
                                                    description=new_description)
            else:
                NumericRoomAttribute.objects.create(name=new_name,
                                                    description=new_description)
            entries['result'].append([OK_RESPONSE])
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

    entries['result'] = []
    if len(entries['old_values']) != len(entries['new_values']):
        # old and new values must have same size
        return entries
    for i in range(len(entries['old_values'])):
        old_name = entries['old_values'][i][0]
        old_description = entries['old_values'][i][1]
        old_attribute_type = entries['old_values'][i][2]
        new_name = entries['new_values'][i][0]
        new_description = entries['new_values'][i][1]
        new_attribute_type = entries['new_values'][i][2]

        if validate_room_attributes_values(new_name, new_description, entries):
            if old_attribute_type != new_attribute_type:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "On ne peut pas changer le type d'un attribut. Supprimez-le et recréez-en un autre."])
            try:
                attribute_to_update = RoomAttribute.objects.get(name=old_name,
                                                                desbription=old_description)
                if old_name != new_name and \
                            RoomAttribute.objects.filter(name=new_name):
                    entries['result'].append(
                        [ERROR_RESPONSE,
                         "Le nom de cet attribut est déjà utilisée."])
                else:
                    attribute_to_update.name = new_name
                    attribute_to_update.description = new_description
                    attribute_to_update.save()
                    entries['result'].append([OK_RESPONSE])
            except RoomAttribute.DoesNotExist:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Un attribut à modifier n'a pas été trouvée dans la base de données."])

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
        old_name = entries['old_values'][i][0]
        old_description = entries['old_values'][i][1]
        try:
            RoomAttribute.objects.get(name=old_name,
                                      description=old_description).delete()
            entries['result'].append([OK_RESPONSE])
        except RoomAttribute.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Un attribut à supprimer n'a pas été trouvé dans la base de données."])
    return entries
