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

from base.models import Room, RoomType
from flopeditor.validator import ERROR_RESPONSE, OK_RESPONSE


def set_rooms(room_type, new_rooms, entries):
    """Adds the rooms to the RoomType

    :param room_type: Room Type to update.
    :type room_type:  base.models.RoomType.
    :param new_rooms: List of rooms to add.
    :type new_rooms:  List
    :param entries: values to create/update (used here only for error reporting).
    :type entries:  django.http.JsonResponse
    :return: True if there is non problem.
    :rtype:  boolean

    """
    members = []
    for room_name in new_rooms:
        room = Room.objects.filter(name=room_name)
        if not room:
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Une salle n'a pas été trouvée dans la base de données.",
                ]
            )
            return False
        members.append(room[0])
    room_type.members.set(members)
    return True


def read(department):
    """Return all room types for a department

    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """

    rooms = Room.objects.filter(departments=department)
    choices = []
    for room in rooms:
        choices.append(room.name)

    room_types = RoomType.objects.filter(department=department)
    values = []
    for room_type in room_types:
        members = []
        for member in room_type.members.all():
            members.append(member.name)
        values.append((room_type.name, members))

    return JsonResponse(
        {
            "columns": [
                {"name": "Catégories", "type": "text", "options": {}},
                {
                    "name": "Groupes et salles concernées",
                    "type": "select-chips",
                    "options": {"values": choices},
                },
            ],
            "values": values,
            "options": {
                "examples": [
                    ["TP", []],
                    ["TD", []],
                    ["Amphi", ["Amphi 1", "Amphi 2", "Amphi 3"]],
                    ["Exam", []],
                ]
            },
        }
    )


def create(entries, department):
    """Create values for room types
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
        new_rooms = entries["new_values"][i][1]
        if not new_name:
            entries["result"].append(
                [ERROR_RESPONSE, "Le nom du type de salle à ajouter est vide."]
            )
        elif len(new_name) > 20:
            entries["result"].append(
                [ERROR_RESPONSE, "Le nom du type de salle à ajouter est trop long."]
            )
        elif RoomType.objects.filter(name=new_name, department=department):
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Le type de salle à ajouter est déjà présent dans la base de données.",
                ]
            )
        else:
            room_type = RoomType.objects.create(name=new_name, department=department)
            if set_rooms(room_type, new_rooms, entries):
                room_type.save()
                entries["result"].append([OK_RESPONSE])
    return entries


def update(entries, department):
    """Update values for room types
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
        old_name = entries["old_values"][i][0]
        new_name = entries["new_values"][i][0]
        new_rooms = entries["new_values"][i][1]
        if not new_name:
            entries["result"].append(
                [ERROR_RESPONSE, "Le nom du type de salle à modifier est vide."]
            )
        elif len(new_name) > 20:
            entries["result"].append(
                [ERROR_RESPONSE, "Le nom du type de salle à modifier est trop long."]
            )
        elif old_name != new_name and RoomType.objects.filter(
            name=new_name, department=department
        ):
            entries["result"].append(
                [ERROR_RESPONSE, "L'abbréviation de ce type de salle est déjà utilisé."]
            )
        else:
            try:
                rt_to_update = RoomType.objects.get(
                    name=old_name, department=department
                )
                rt_to_update.name = new_name
                if set_rooms(rt_to_update, new_rooms, entries):
                    rt_to_update.save()
                    entries["result"].append([OK_RESPONSE])
            except RoomType.DoesNotExist:
                entries["result"].append(
                    [
                        ERROR_RESPONSE,
                        "Un type de salle à modifier n'a pas été trouvé dans la base de données.",
                    ]
                )

    return entries


def delete(entries, department):
    """Delete values for room types
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
            RoomType.objects.get(name=old_name, department=department).delete()
            entries["result"].append([OK_RESPONSE])
        except RoomType.DoesNotExist:
            entries["result"].append(
                [
                    ERROR_RESPONSE,
                    "Un type de salle à supprimer n'a pas été trouvé dans la base de données.",
                ]
            )
    return entries
