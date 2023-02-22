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
from base.models import Room, Department, RoomAttribute, BooleanRoomAttributeValue, NumericRoomAttributeValue
from flopeditor.validator import OK_RESPONSE, ERROR_RESPONSE

attributes_list = [] # list(RoomAttribute.objects.all())

def set_values_for_room(room, i, new_name, entries):
    """
    :param room: Room to add/update.
    :type department:  base.models.Department
    :return: False in case of problem. True instead.
    :rtype:  Boolean

    """
    subrooms = []
    for subroom_name in entries['new_values'][i][1]:
        subrooms_found = Room.objects.filter(name=subroom_name)
        if subrooms_found[0].name == new_name:
            entries['result'].append([
                ERROR_RESPONSE,
                "Une salle ne peut pas être sur-salle d'elle-même."
            ])
            return False
        if len(subrooms_found) != 1:
            entries['result'].append([
                ERROR_RESPONSE,
                "Erreur en base de données."
            ])
            return False
        subrooms.append(subrooms_found[0])
    depts = []
    for dept_abbrev in entries['new_values'][i][2]:
        depts_found = Department.objects.filter(abbrev=dept_abbrev)
        if len(depts_found) != 1:
            entries['result'].append([
                ERROR_RESPONSE,
                "Erreur en base de données."
            ])
            return False
        depts.append(depts_found[0])
    room.name = new_name
    room.subrooms.set(subrooms)
    room.departments.set(depts)
    return True


def has_rights_to_create_or_delete_room(user, room, entries):
    """
    :param user: User trying to create or delete a room.
    :type user:  people.models.User
    :param room: Room to add/delete.
    :type room:  base.models.Room
    :return: True if user has rights.
    :rtype:  Boolean

    """
    for dept in room.departments.all():
        if not user.has_department_perm(department=dept, admin=True):
            entries['result'].append([
                ERROR_RESPONSE,
                "Vous ne pouvez pas créer ou supprimer une salle avec un département (" +
                dept.name+") dont vous n'êtes pas responsable."
            ])
            return False
    return True


def has_rights_to_update_room(user, entries, i):
    """
    :param user: User trying to create or delete a room.
    :type user:  people.models.User
    :param entries: flopeditor list.
    :type room:  list
    :return: True if user has rights.
    :rtype:  Boolean

    """
    if set(entries['new_values'][i][2]) == set(entries['old_values'][i][2]):
        departments = Department.objects.filter(
            abbrev__in=entries['new_values'][i][2])
        if not departments:
            return True
        for dept in departments:
            if user.has_department_perm(department=dept, admin=True):
                return True
        entries['result'].append([
            ERROR_RESPONSE,
            "Vous ne pouvez pas modifier une salle dont vous n'êtes pas responsable."
        ])
        return False

    old_departments = Department.objects.filter(
        abbrev__in=entries['old_values'][i][2])

    new_departments = Department.objects.filter(
        abbrev__in=entries['new_values'][i][2])

    for dep in old_departments:
        if not user.has_department_perm(department=dep, admin=True) and dep not in new_departments:
            entries['result'].append([
                ERROR_RESPONSE,
                "Impossible de retirer d'une salle un départment dont vous n'êtes pas responsable."
            ])
            return False

    for dep in new_departments:
        if not user.has_department_perm(department=dep, admin=True) and dep not in old_departments:
            entries['result'].append([
                ERROR_RESPONSE,
                "impossible d'ajouter à une salle un départment dont vous n'êtes pas responsable."
            ])
            return False

    return True


def room_attribute_values(room):
    result_list = []
    for attribute in attributes_list:
        if attribute.is_boolean():
            try:
                attribute_value = BooleanRoomAttributeValue.objects.get(room=room,
                                                                        attribute=attribute.booleanroomattribute).value
            except BooleanRoomAttributeValue.DoesNotExist:
                attribute_value = None
        else:
            try:
                attribute_value = NumericRoomAttributeValue.objects.get(room=room,
                                                                        attribute=attribute.numericroomattribute).value
            except NumericRoomAttributeValue.DoesNotExist:
                attribute_value = None
        result_list.append(attribute_value)
    return result_list

def read():
    """Return all rooms
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    # Chips options
    rooms_available = list(Room.objects.values_list('name', flat=True))
    departments = list(Department.objects.values_list('abbrev', flat=True))

    # Rows
    rooms = Room.objects.all()
    values = []
    for room in rooms:
        subrooms = []
        for subroom in room.subrooms.all():
            subrooms.append(subroom.name)
        room_departments = []
        for dept in room.departments.all():
            room_departments.append(dept.abbrev)
        value = [room.name, subrooms, room_departments]
        value += room_attribute_values(room)
        values.append(tuple(value))

    attributes_columns = [
                {'name': attribute.name,
                 "type": "select" if attribute.is_boolean() else "int",
                 "options": {"values": [True, False]} if attribute.is_boolean() else {}}
        for attribute in attributes_list]

    columns = [{
            'name': 'Nom',
            "type": "text",
            "options": {}
        }, {
            'name': 'Sous-salles',
            "type": "select-chips",
            "options": {'values': rooms_available}
        }, {
            'name': 'Départements associés',
            "type": "select-chips",
            "options": {'values': departments}
        }] + attributes_columns

    return JsonResponse({
        "columns":  columns,
        "values": values,
        "options": {
            "examples": []
        }
    })


def create(request, entries):
    """Create values for rooms
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
        if not new_name:
            entries['result'].append([ERROR_RESPONSE,
                                      "Le nom de la salle ne peut pas être vide."])
        elif len(new_name) > 20:
            entries['result'].append([ERROR_RESPONSE,
                                      "Le nom de la salle est trop long."])
        elif Room.objects.filter(name=new_name):
            entries['result'].append([
                ERROR_RESPONSE,
                "La salle à ajouter est déjà présente dans la base de données."
            ])
        else:
            room = Room.objects.create(name=new_name)
            if set_values_for_room(room, i, new_name, entries) and \
                    has_rights_to_create_or_delete_room(request.user, room, entries):
                room.save()
                for attribute_rank, attribute in enumerate(attributes_list):
                    attribute_value = entries['new_values'][i][attribute_rank+2]
                    if attribute_value is not None:
                        if attribute.is_boolean():
                            BooleanRoomAttributeValue.objects.create(room=room,
                                                                     attribute=attribute.booleanroomattribute,
                                                                     value=attribute_value)
                        else:
                            NumericRoomAttributeValue.objects.create(room=room,
                                                                     attribute=attribute.numericroomattribute,
                                                                     value=attribute_value)
                entries['result'].append([OK_RESPONSE])
            else:
                room.delete()

    return entries


def update(request, entries):
    """Update values for rooms
    :param entries: Values to modify.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    if len(entries['old_values']) != len(entries['new_values']):
        return entries

    entries['result'] = []
    for i in range(len(entries['old_values'])):
        old_name = entries['old_values'][i][0]
        new_name = entries['new_values'][i][0]
        if not has_rights_to_update_room(request.user, entries, i):
            pass
        elif not new_name:
            entries['result'].append([ERROR_RESPONSE,
                                      "Le nouveau nom de la salle ne peut pas être vide."])
        elif len(new_name) > 20:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Le nom de la salle est trop long."])
        elif Room.objects.filter(name=new_name) and old_name != new_name:
            entries['result'].append([
                ERROR_RESPONSE,
                "La salle à modifier est déjà présente dans la base de données."
            ])
        else:
            try:
                room_to_update = Room.objects.get(name=old_name)
                if set_values_for_room(room_to_update, i, new_name, entries):
                    room_to_update.save()
                    for attribute_rank, attribute in enumerate(attributes_list):
                        attribute_value = entries['new_values'][i][attribute_rank + 2]
                        if attribute_value is not None:
                            if attribute.is_boolean():
                                attribute, created = BooleanRoomAttributeValue\
                                    .objects.get_or_create(room=room_to_update,attribute=attribute.booleanroomattribute)
                                attribute.value = attribute_value
                                attribute.save()
                            else:
                                attribute, created = NumericRoomAttributeValue \
                                    .objects.get_or_create(room=room_to_update,
                                                           attribute=attribute.numericroomattribute)
                                attribute.value = attribute_value
                                attribute.save()
                    entries['result'].append([OK_RESPONSE])
            except Room.DoesNotExist:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Une salle à modifier n'a pas été trouvée dans la base de données."])
    return entries


def delete(request, entries):
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
        try:
            room = Room.objects.get(name=old_name)
            if has_rights_to_create_or_delete_room(request.user, room, entries):
                room.delete()
                entries['result'].append([OK_RESPONSE])

        except Room.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Une salle à supprimer n'a pas été trouvée dans la base de données."])
    return entries
