# -*- coding: utf-8 -*-

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

from django.db.models import Q


from base.models import SchedulingPeriod, TimetableVersion
from core.decorators import timer
from TTapp.flop_constraint import FlopConstraint, all_subclasses


@timer
def are_all_flop_constraints_satisfied_for(
    period: SchedulingPeriod,
    version: TimetableVersion,
    strong_constraints_only: bool = False,
    active_only: bool = True,
):
    errors = []
    for cl in all_subclasses(FlopConstraint):
        considered_objects = cl.objects.filter(
            Q(periods__isnull=True) | Q(periods=period), department=version.department
        )
        if strong_constraints_only:
            considered_objects = considered_objects.filter(weight=None)
        if active_only:
            considered_objects = considered_objects.filter(is_active=True)
        for a in considered_objects:
            try:
                a.is_satisfied_for(period, version)
            except NotImplementedError:
                continue
            except AssertionError as e:
                errors.append(e)
    return errors
