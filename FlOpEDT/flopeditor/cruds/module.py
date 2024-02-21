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
from base.models import Module, TrainingPeriod, TrainingProgramme
from displayweb.models import ModuleDisplay
from people.models import Tutor
from flopeditor.validator import OK_RESPONSE, ERROR_RESPONSE, validate_module_values


def read(department):
    """Return all modules for a department

    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """

    modules = Module.objects.filter(
        train_prog__in=TrainingProgramme.objects.filter(department=department))

    values = []
    for module in modules:
        if module.head is None:
            head = ""
        else:
            head = module.head.username
        values.append(
            (
                module.abbrev,
                module.ppn,
                module.name,
                module.description,
                module.train_prog.name,
                head,
                module.period.name,
            )
        )
    return JsonResponse(
        {
            "columns": [
                {"name": "Abréviation", "type": "text", "options": {}},
                {"name": "Code PPN", "type": "text", "options": {}},
                {"name": "Nom complet", "type": "text", "options": {}},
                {"name": "Description", "type": "text", "options": {}},
                {
                    "name": "Promo",
                    "type": "select",
                    "options": {
                        "values": [
                            *TrainingProgramme.objects.filter(
                                department=department
                            ).values_list("name", flat=True)
                        ]
                    },
                },
                {
                    "name": "Enseignant·e responsable",
                    "type": "select",
                    "options": {
                        "values": [
                            *Tutor.objects.filter(departments=department).values_list(
                                "username", flat=True
                            )
                        ]
                    },
                },
                {
                    "name": "Semestre",
                    "type": "select",
                    "options": {
                        "values": [
                            *TrainingPeriod.objects.filter(
                                department=department
                            ).values_list("name", flat=True)
                        ]
                    },
                },
            ],
            "values": values,
        }
    )


def create(entries, department):
    """Create values for modules
    :param entries: Values to create.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """

    entries['result'] = []
    for i in range(len(entries['new_values'])):
        if not validate_module_values(entries['new_values'][i], entries):
            pass
        elif Module.objects.filter(
                abbrev=entries['new_values'][i][0],
                train_prog__in=TrainingProgramme.objects.filter(department=department)):
            entries['result'].append([
                ERROR_RESPONSE,
                "Un module de ce nom existe déjà dans ce départment"
            ])
        else:
            try:
                module = Module.objects.create(
                    abbrev=entries['new_values'][i][0],
                    ppn=entries['new_values'][i][1],
                    name=entries['new_values'][i][2],
                    description=entries['new_values'][i][3],
                    train_prog=TrainingProgramme.objects.get(
                        name=entries["new_values"][i][4], department=department
                    ),
                    head=Tutor.objects.get(username=entries["new_values"][i][5]),
                    period=TrainingPeriod.objects.get(
                        name=entries["new_values"][i][6], department=department
                    ),
                )
                mod_disp = ModuleDisplay(module=module)
                mod_disp.save()
                entries["result"].append([OK_RESPONSE])
            except (
                TrainingProgramme.DoesNotExist,
                Tutor.DoesNotExist,
                TrainingPeriod.DoesNotExist,
            ):
                entries["result"].append([ERROR_RESPONSE, "Erreur en base de données"])
    return entries


def update(entries, department):
    """Update values for modules
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

    for i in range(len(entries['new_values'])):
        if validate_module_values(entries['new_values'][i], entries):
            try:
                module = Module.objects.get(
                    abbrev=entries['old_values'][i][0],
                    train_prog__in=TrainingProgramme.objects.filter(department=department))

                if entries['old_values'][i][0] != entries['new_values'][i][0] and \
                    Module.objects.filter(abbrev=entries['new_values'][i][0],
                                          train_prog__in=TrainingProgramme
                                          .objects.filter(department=department)):

                    entries['result'].append([
                        ERROR_RESPONSE,
                        "Un module de ce nom existe déjà dans ce départment"
                    ])
                else:
                    module.abbrev = entries['new_values'][i][0]
                    module.ppn = entries['new_values'][i][1]
                    module.name = entries['new_values'][i][2]
                    module.description = entries['new_values'][i][3]
                    module.train_prog = TrainingProgramme.objects.get(
                        name=entries['new_values'][i][4], department=department)
                    module.head = Tutor.objects.get(
                        username=entries["new_values"][i][5]
                    )
                    module.period = TrainingPeriod.objects.get(
                        name=entries["new_values"][i][6], department=department
                    )
                    module.save()
                    entries["result"].append([OK_RESPONSE])
            except (
                Module.DoesNotExist,
                TrainingProgramme.DoesNotExist,
                Tutor.DoesNotExist,
                TrainingPeriod.DoesNotExist,
            ):
                entries["result"].append([ERROR_RESPONSE, "Erreur en base de données"])

    return entries


def delete(entries, department):
    """Delete values for modules
    :param entries: Values to delete.
    :type entries:  django.http.JsonResponse
    :param department: Department.
    :type department:  base.models.Department
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse
    """
    entries['result'] = []
    for i in range(len(entries['old_values'])):
        old_abbrev = entries['old_values'][i][0]
        try:
            Module.objects.get(abbrev=old_abbrev, train_prog__in=TrainingProgramme.objects.filter(
                department=department)).delete()
        except Module.DoesNotExist:
            entries['result'].append(
                [ERROR_RESPONSE,
                 "Un module à supprimer n'a pas été trouvé dans la base de données."])

    return entries
