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

from base.models import (GroupType, StructuralGroup, TrainingProgramme,
                         TransversalGroup)
from flopeditor.validator import (ERROR_RESPONSE, OK_RESPONSE,
                                  validate_student_transversal_groups_values)


def read(department):
    """Return all student groups in the department

    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    training_programmes = TrainingProgramme.objects.filter(department=department)
    group_types = GroupType.objects.filter(department=department)
    transversal_groups = TransversalGroup.objects.filter(
        train_prog__in=training_programmes)
    structural_groups = StructuralGroup.objects.filter(
        train_prog__in=training_programmes)

    values = []
    train_prog_choices = [tp.abbrev for tp in training_programmes]
    type_choices = [type_choice.name for type_choice in group_types]
    parallel_groups_choices = [g.name for g in transversal_groups]    #STAGE Empêcher de mettre le groupe en parallèle avec lui même (je ne sais pas si c'est ici)
    conflicting_groups_choices = [g.name for g in structural_groups]
    for group in transversal_groups:
        parallel_groups = [p.name for p in group.parallel_groups.all()]
        conflicting_groups = [c.name for c in group.conflicting_groups.all()]
        
        values.append((group.name, group.train_prog.abbrev,
                       conflicting_groups, parallel_groups, 
                       group.type.name if group.type is not None else None, group.size))
		
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
            'name': 'En conflit avec...',
            "type": "select-chips",
            "options": {
                "values": conflicting_groups_choices
            }
        }, {
            'name': 'Parallèle à...',
            "type": "select-chips",
            "options": {
                "values": parallel_groups_choices
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
        new_type_name = entries['new_values'][i][4]
        size = entries['new_values'][i][5]

        try:
            train = TrainingProgramme.objects.get(
                abbrev=new_tp_abbrev, department=department)
            gtype = GroupType.objects.get(
                name=new_type_name, department=department)
            new_conflicting_groups = []
            for group_name in entries['new_values'][i][2]:
                new_conflicting_groups.append(StructuralGroup.objects.get(
                    name=group_name, train_prog=train))
            new_parallel_groups = []
            for group_name in entries['new_values'][i][3]:
                new_parallel_groups.append(TransversalGroup.objects.get(
                    name=group_name, train_prog=train))

            if validate_student_transversal_groups_values(entries['new_values'][i], entries):
                if TransversalGroup.objects.filter(name=new_name, train_prog=train).exists() \
                        or StructuralGroup.objects.filter(name=new_name, train_prog=train).exists():
                    entries['result'].append([
                        ERROR_RESPONSE,
                        "un groupe de ce nom existe déjà dans cette promo."
                    ])
                else:

                    group = TransversalGroup.objects.create(
                        name=new_name,
                        size=size,
                        train_prog=train,
                        type=gtype)

                    for conflict in new_conflicting_groups:
                        group.conflicting_groups.add(conflict)

                    for parallel in new_parallel_groups:
                        group.parallel_groups.add(parallel)


                    group.save()
                    entries['result'].append([OK_RESPONSE])

        except (TrainingProgramme.DoesNotExist, GroupType.DoesNotExist):
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Erreur en base de données."])

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
        if not validate_student_transversal_groups_values(entries['new_values'][i], entries):
            return entries

        old_name = entries['old_values'][i][0]
        old_tp_abbrev = entries['old_values'][i][1]

        new_name = entries['new_values'][i][0]
        new_tp_abbrev = entries['new_values'][i][1]
        new_type_name = entries['new_values'][i][4]

        try:
            old_train = TrainingProgramme.objects.get(
                abbrev=old_tp_abbrev, department=department)
            new_train = TrainingProgramme.objects.get(
                abbrev=new_tp_abbrev, department=department)
            new_gtype = GroupType.objects.get(
                name=new_type_name, department=department)

            if (new_name != old_name or new_tp_abbrev != old_tp_abbrev) and \
                    (TransversalGroup.objects.filter(name=new_name, train_prog=new_train).exists()
                        or StructuralGroup.objects.filter(name=new_name, train_prog=new_train).exists()):
                entries['result'].append([
                    ERROR_RESPONSE,
                    "un groupe de ce nom existe déjà dans cette promo."
                ])
                return entries

            group = TransversalGroup.objects.get(name=old_name, train_prog=old_train)
            group.train_prog = new_train
            group.name = new_name
            group.size = entries['new_values'][i][5]
            group.type = new_gtype

            group.conflicting_groups.remove(*group.conflicting_groups.all())
            for group_name in entries['new_values'][i][2]:
                conflict = StructuralGroup.objects.get(
                    name=group_name, train_prog=new_train)
                group.conflicting_groups.add(conflict)

            group.parallel_groups.remove(*group.parallel_groups.all())
            for group_name in entries['new_values'][i][3]:
                parallel = TransversalGroup.objects.get(
                    name=group_name, train_prog=new_train)
                group.parallel_groups.add(parallel)

            group.save()
            entries['result'].append([OK_RESPONSE])

        except (TrainingProgramme.DoesNotExist, GroupType.DoesNotExist):
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Erreur en base de données."])

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
            TransversalGroup.objects.get(name=old_name, train_prog=train).delete()
            entries['result'].append([OK_RESPONSE])
        except (GroupType.DoesNotExist, TrainingProgramme.DoesNotExist):
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Erreur en base de données."])
    return entries
