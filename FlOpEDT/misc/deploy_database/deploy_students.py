# coding: utf-8
# !/usr/bin/python

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

import csv

from django.db import transaction

from base.models import StructuralGroup
from people.models import Student, UserDepartmentSettings


@transaction.atomic
def extract_students_file(file_name, department, train_prog):
    file = open(file_name)
    reader = csv.DictReader(file)
    for row in reader:
        last_name = row["nom"]
        first_name = row["prenom"]
        email = row["email"]
        gp_name = row["groupe"]
        username = email.split("@")[0]
        group = StructuralGroup.objects.get(train_prog=train_prog, name=gp_name)
        S, created = Student.objects.get_or_create(username=username)
        S.first_name = first_name
        S.last_name = last_name
        S.email = email
        S.save()
        if created:
            S.set_password("patate_en_carton")
        S.generic_groups.clear()
        S.generic_groups.add(group)
        S.is_student = True
        S.save()
        UserDepartmentSettings(user=S, department=department).save()
