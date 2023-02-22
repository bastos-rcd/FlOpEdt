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
from base.models import StructuralGroup, TrainingProgramme, GroupType, TransversalGroup
from flopeditor.validator import OK_RESPONSE, ERROR_RESPONSE, validate_student_structural_groups_values


def read(department):
    """Return all student groups in the department

    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    groups = StructuralGroup.objects.filter(
        train_prog__in=TrainingProgramme.objects.filter(department=department))
    values = []
    parents_choices = []
    for group in groups:
        parents = []
        for parent in group.parent_groups.all():
            parents.append(parent.name)
        values.append((group.name, group.train_prog.abbrev,
                       parents, group.type.name, group.size))
        parents_choices.append(group.name)

    train_prog_choices = []
    for training_p in TrainingProgramme.objects.filter(department=department):
        train_prog_choices.append(training_p.abbrev)

    type_choices = []
    for type_choice in GroupType.objects.filter(department=department):
        type_choices.append(type_choice.name)

    return JsonResponse({
        "columns":  [{
            'name': 'Nom',
            "type": "text",
            "options": {}
        }, {
            'name': 'Promo',
            "type": "select",
            "options": {
                "values": train_prog_choices
            }
        }, {
            'name': 'Sous-groupe de...',
            "type": "select-chips",
            "options": {
                "values": parents_choices
            }
        }, {
            'name': 'Nature',
            "type": "select",
            "options": {
                "values": type_choices
            }
        }, {
            'name': 'Taille',
            "type": "int",
            "options": {}
        }],
        "values": values
    })


def create(entries, department):
    """Create values for group type in the department
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
        new_tp_abbrev = entries['new_values'][i][1]
        new_type_name = entries['new_values'][i][3]

        try:
            train = TrainingProgramme.objects.get(
                abbrev=new_tp_abbrev, department=department)
            gtype = GroupType.objects.get(
                name=new_type_name, department=department)
            new_parents = []
            for group_name in entries['new_values'][i][2]:
                new_parents.append(StructuralGroup.objects.get(
                    name=group_name, train_prog=train))

            if validate_student_structural_groups_values(entries['new_values'][i], entries):
                if TransversalGroup.objects.filter(name=new_name, train_prog=train).exists() \
                        or StructuralGroup.objects.filter(name=new_name, train_prog=train).exists():
                    entries['result'].append([
                        ERROR_RESPONSE,
                        "un groupe de ce nom existe déjà dans cette promo."
                    ])
                else:

                    group = StructuralGroup.objects.create(
                        name=new_name,
                        size=entries['new_values'][i][4],
                        train_prog=train,
                        type=gtype)
                    group.basic = True

                    for parent in new_parents:
                        group.basic = False
                        group.parent_groups.add(parent)

                    group.save()
                    entries['result'].append([OK_RESPONSE])

        except (TrainingProgramme.DoesNotExist, GroupType.DoesNotExist):
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Erreur en base de données."])
        except StructuralGroup.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Un groupe ne peut-être le sous-groupe que d'un groupe de la même promo."])

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
    entries['result'] = []
    if len(entries['old_values']) != len(entries['new_values']):
        return entries

    for i in range(len(entries['old_values'])):
        if not validate_student_structural_groups_values(entries['new_values'][i], entries):
            return entries

        old_name = entries['old_values'][i][0]
        old_tp_abbrev = entries['old_values'][i][1]

        new_name = entries['new_values'][i][0]
        new_tp_abbrev = entries['new_values'][i][1]
        new_type_name = entries['new_values'][i][3]

        try:
            old_train = TrainingProgramme.objects.get(
                abbrev=old_tp_abbrev, department=department)
            new_train = TrainingProgramme.objects.get(
                abbrev=new_tp_abbrev, department=department)
            new_gtype = GroupType.objects.get(
                name=new_type_name, department=department)

            if (new_name != old_name or new_tp_abbrev != old_tp_abbrev) and \
            StructuralGroup.objects.filter(name=new_name, train_prog=new_train):
                entries['result'].append([
                    ERROR_RESPONSE,
                    "un groupe de ce nom existe déjà dans cette promo."
                ])
                return entries

            group = StructuralGroup.objects.get(name=old_name, train_prog=old_train)
            group.train_prog = new_train
            group.name = new_name
            group.size = entries['new_values'][i][4]
            group.type = new_gtype
            group.basic = True

            group.parent_groups.remove(*group.parent_groups.all())
            for group_name in entries['new_values'][i][2]:
                group.basic = False
                parent = StructuralGroup.objects.get(
                    name=group_name, train_prog=new_train)
                group.parent_groups.add(parent)

            group.save()
            entries['result'].append([OK_RESPONSE])

        except (TrainingProgramme.DoesNotExist, GroupType.DoesNotExist):
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Erreur en base de données."])

        except StructuralGroup.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Un groupe ne peut-être le sous-groupe que d'un groupe de la même promo."])

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

    entries['result'] = []
    for i in range(len(entries['old_values'])):
        old_name = entries['old_values'][i][0]
        old_tp_abbrev = entries['old_values'][i][1]
        try:
            train = TrainingProgramme.objects.get(
                abbrev=old_tp_abbrev, department=department)
            StructuralGroup.objects.get(name=old_name, train_prog=train).delete()
            entries['result'].append([OK_RESPONSE])
        except (GroupType.DoesNotExist, TrainingProgramme.DoesNotExist):
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Erreur en base de données."])
    return entries
