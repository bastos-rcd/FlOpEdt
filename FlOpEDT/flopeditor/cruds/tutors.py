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
from base.models import Department
from base.preferences import split_preferences
from people.models import Tutor, SupplyStaff, User, FullStaff, BIATOS
from flopeditor.validator import OK_RESPONSE, ERROR_RESPONSE, validate_tutor_values
from flopeditor.db_requests import get_status_of_tutor, TUTOR_CHOICES_LIST, TUTOR_CHOICES_DICT

# rank in this list == bit's position in user.rights
RIGHTS_LIST = [
    "Quand 'modifier Cours' coché, les cours sont colorés avec la dispo de l'intervenant",
    "Peut changer les dispos de tout le monde",
    "Peut modifier l'emploi du temps comme bon lui semble",
    "Si responsable d'un module, peut changer les dispos des vacataires de ce module",
    "Peut surpasser les contraintes lors de la modification de cours"
]

def user_rights_to_list(rights):
    """Convert User.rights integer to list of string
    :param rights: rights integer.
    :type rights:  int
    :return: List containing the corresponding rights.
    :rtype:  list
    """
    result = []
    for (i, right) in enumerate(RIGHTS_LIST):
        if (rights >> i) % 2 == 1:
            result.append(right)
    return result

def list_to_user_rights(right_list):
    """Convert list of rights to User.rights integer
    :param right_list: List containing the user's rights.
    :type right_list:  list
    :return: rights integer
    :rtype:  int
    """
    rights = 0
    for (i, right) in enumerate(RIGHTS_LIST):
        if right in right_list:
            rights += 2**i
    return rights


def has_rights_to_delete_tutor(user, tutor, entries):
    """
    :param user: User trying to create or delete a tutor.
    :type user:  people.models.User
    :param tutor: Tutor to add/delete.
    :type tutor:  base.models.Room
    :return: True if user has rights.
    :rtype:  Boolean
    """

    if user.username == tutor.username:
        entries['result'].append(
            [ERROR_RESPONSE,
             "Vous ne pouvez pas vous supprimer vous-même."])
        return False
    if not user.is_superuser and tutor.is_superuser:
        entries['result'].append(
            [ERROR_RESPONSE,
             "Vous n'avez pas les droits nécessaires pour supprimer cet utilisateur."])
        return False
    for dept in tutor.departments.all():
        if not user.has_department_perm(department=dept, admin=True):
            entries['result'].append([
                ERROR_RESPONSE,
                "Vous ne pouvez pas supprimer un·e intervenant·e avec un département (" +
                dept.name+") dont vous n'êtes pas responsable."
            ])
            return False
    return True


def has_rights_to_create_tutor(user, tutor, entries):
    """
    :param user: User trying to create or delete a tutor.
    :type user:  people.models.User
    :param tutor: Tutor to add/delete.
    :type tutor:  base.models.Room
    :return: True if user has rights.
    :rtype:  Boolean
    """

    for dept in tutor.departments.all():
        if not user.has_department_perm(department=dept, admin=True):
            entries['result'].append([
                ERROR_RESPONSE,
                "Vous ne pouvez pas créer un·e intervenant·e avec un département (" +
                dept.name+") dont vous n'êtes pas responsable."
            ])
            return False
    return True


def has_rights_to_update_tutor(user, entries, i):
    """
    :param user: User trying to create or delete a tutor.
    :type user:  people.models.User
    :param entries: flopeditor list.
    :type room:  list
    :return: True if user has rights.
    :rtype:  Boolean

    """
    if set(entries['new_values'][i][8]) == set(entries['old_values'][i][8]):
        departments = Department.objects.filter(
            name__in=entries['new_values'][i][8])
        if not departments:
            return True
        for dept in departments:
            if user.has_department_perm(department=dept, admin=True):
                return True
        entries['result'].append([
            ERROR_RESPONSE,
            "Vous ne pouvez pas modifier un·e intervenant·e dont vous n'êtes pas responsbale."
        ])
        return False

    old_departments = Department.objects.filter(
        name__in=entries['old_values'][i][8])

    new_departments = Department.objects.filter(
        name__in=entries['new_values'][i][8])

    for dep in old_departments:
        if not user.has_department_perm(department=dep, admin=True) and dep not in new_departments:
            entries['result'].append([
                ERROR_RESPONSE,
                "Impossible de retirer d'un intervenant" +
                " un département dont vous n'êtes pas responsable."
            ])
            return False

    for dep in new_departments:
        if not user.has_department_perm(department=dep, admin=True) and dep not in old_departments:
            entries['result'].append([
                ERROR_RESPONSE,
                "Impossible d'ajouter à un·e intervenant·e" +
                " un département dont vous n'êtes pas responsable."
            ])
            return False

    return True


def read():
    """Return all rooms
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """

    tutors = Tutor.objects.all()
    values = []
    for tut in tutors:
        status, position, employer = get_status_of_tutor(tut)
        values.append((
            tut.username,
            tut.first_name,
            tut.last_name,
            status,
            tut.email,
            position,
            employer,
            user_rights_to_list(tut.rights),
            list(tut.departments.values_list('name', flat=True))
        ))

    return JsonResponse({
        "columns":  [{
            'name': 'Id',
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
            'name': 'Statut',
            "type": "select",
            "options": {'values': TUTOR_CHOICES_LIST}
        }, {
            'name': 'Email',
            "type": "text",
            "options": {}
        }, {
            'name': 'Position',
            "type": "text",
            "options": {}
        }, {
            'name': 'Employeur',
            "type": "text",
            "options": {}
        }, {
            'name': 'Droits particuliers',
            "type": "select-chips",
            "options": {'values': RIGHTS_LIST}
        }, {
            'name': 'Départements',
            "type": 'select-chips',
            "options": {'values': list(Department.objects.values_list('name', flat=True))}
        }],
        "values": values,
        "options": {
            "deleteMessage": "Supprimer une·e intervenant·e supprime également tous les cours " +
                             "qui lui sont associés."
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
        if not validate_tutor_values(entries['new_values'][i], entries):
            pass
        elif User.objects.filter(username=entries['new_values'][i][0]):
            entries['result'].append([
                ERROR_RESPONSE,
                "Id déjà utilisé par quelqu'un·e d'autre."
            ])
        else:
            tutor = None

            if entries['new_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.SUPP_STAFF]:
                tutor = SupplyStaff.objects.create(
                    username=entries['new_values'][i][0],
                    first_name=entries['new_values'][i][1],
                    last_name=entries['new_values'][i][2],
                    status=Tutor.SUPP_STAFF,
                    email=entries['new_values'][i][4],
                    position=entries['new_values'][i][5],
                    employer=entries['new_values'][i][6],
                    is_tutor=True,
                    rights=list_to_user_rights(entries['new_values'][i][7]))
            elif entries['new_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.FULL_STAFF]:
                tutor = FullStaff.objects.create(
                    username=entries['new_values'][i][0],
                    first_name=entries['new_values'][i][1],
                    last_name=entries['new_values'][i][2],
                    status=Tutor.FULL_STAFF,
                    email=entries['new_values'][i][4],
                    is_tutor=True,
                    rights=list_to_user_rights(entries['new_values'][i][7]))
            elif entries['new_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.BIATOS]:
                tutor = BIATOS.objects.create(
                    username=entries['new_values'][i][0],
                    first_name=entries['new_values'][i][1],
                    last_name=entries['new_values'][i][2],
                    status=Tutor.BIATOS,
                    email=entries['new_values'][i][4],
                    rights=list_to_user_rights(entries['new_values'][i][7]))

            tutor.departments.set(Department.objects.filter(
                name__in=entries['new_values'][i][8]))

            if has_rights_to_create_tutor(request.user, tutor, entries):
                tutor.save()
                split_preferences(tutor)
                entries['result'].append([OK_RESPONSE])
            else:
                tutor.delete()
    return entries


def update(request, entries):
    """Update values for tutors
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
        if not has_rights_to_update_tutor(request.user, entries, i):
            pass
        elif not validate_tutor_values(entries['new_values'][i], entries):
            pass
        elif User.objects.filter(username=entries['new_values'][i][0]) and \
                entries['old_values'][i][0] != entries['new_values'][i][0]:
            entries['result'].append([
                ERROR_RESPONSE,
                "Id déjà utilisé par quelqu'un·e d'autre."
            ])
        else:
            try:
                tutor_to_update = Tutor.objects.get(
                    username=entries['old_values'][i][0])
                old_departments = set(tutor_to_update.departments.all())
                new_departments = Department.objects.filter(name__in=entries['new_values'][i][8])
                if entries['new_values'][i][3] != entries['old_values'][i][3]:
                    if entries['new_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.SUPP_STAFF]:
                        new = SupplyStaff(tutor_ptr_id=tutor_to_update.id)
                        new.__dict__.update(tutor_to_update.__dict__)
                        new.status = Tutor.SUPP_STAFF
                        new.position = entries['new_values'][i][5]
                        new.employer = entries['new_values'][i][6]
                    elif entries['new_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.FULL_STAFF]:
                        new = FullStaff(tutor_ptr_id=tutor_to_update.id)
                        new.__dict__.update(tutor_to_update.__dict__)
                        new.status = Tutor.FULL_STAFF
                    else:
                        new = BIATOS(tutor_ptr_id=tutor_to_update.id)
                        new.__dict__.update(tutor_to_update.__dict__)
                        new.status = Tutor.BIATOS

                    new.username = entries['new_values'][i][0]
                    new.first_name = entries['new_values'][i][1]
                    new.last_name = entries['new_values'][i][2]
                    new.email = entries['new_values'][i][4]
                    new.rights = list_to_user_rights(entries['new_values'][i][7])
                    new.departments.set(new_departments)
                    new.save()

                    if entries['old_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.SUPP_STAFF]:
                        SupplyStaff.objects.get(id=tutor_to_update.id).delete(keep_parents=True)
                    elif entries['old_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.FULL_STAFF]:
                        FullStaff.objects.get(id=tutor_to_update.id).delete(keep_parents=True)
                    else:
                        BIATOS.objects.get(id=tutor_to_update.id).delete(keep_parents=True)
                else:
                    if entries['new_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.SUPP_STAFF]:
                        tutor_to_update.status = Tutor.SUPP_STAFF
                        tutor_to_update = SupplyStaff.objects.get(
                            username=entries['old_values'][i][0])
                        tutor_to_update.position = entries['new_values'][i][5]
                        tutor_to_update.employer = entries['new_values'][i][6]
                    elif entries['new_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.FULL_STAFF]:
                        tutor_to_update.status = Tutor.FULL_STAFF
                    elif entries['new_values'][i][3] == TUTOR_CHOICES_DICT[Tutor.BIATOS]:
                        tutor_to_update.status = Tutor.BIATOS

                    tutor_to_update.username = entries['new_values'][i][0]
                    tutor_to_update.first_name = entries['new_values'][i][1]
                    tutor_to_update.last_name = entries['new_values'][i][2]
                    tutor_to_update.email = entries['new_values'][i][4]
                    tutor_to_update.rights = list_to_user_rights(entries['new_values'][i][7])
                    tutor_to_update.departments.set(new_departments)
                    tutor_to_update.save()
                    new = tutor_to_update

                if old_departments != set(new_departments):
                    split_preferences(new)
                entries['result'].append([OK_RESPONSE])
            except Tutor.DoesNotExist:
                entries['result'].append(
                    [ERROR_RESPONSE,
                     "Un intervenant à modifier n'a pas été trouvée dans la base de données."])
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
        username = entries['old_values'][i][0]
        try:
            tutor = Tutor.objects.get(username=username)

            if has_rights_to_delete_tutor(request.user, tutor, entries):
                tutor.delete()
                entries['result'].append([OK_RESPONSE])

        except Tutor.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Un intervenant à supprimer n'a pas été trouvé dans la base de données."])
    return entries
