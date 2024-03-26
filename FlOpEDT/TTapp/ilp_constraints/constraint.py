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

from collections.abc import Iterable

from base.timing import get_all_scheduling_periods
from TTapp.ilp_constraints.constraint_type import ConstraintType


def sing_or_plural(dimension):
    plurial = ""
    if len(dimension["value"]) >= 2 and dimension["display"][-1] != "s":
        plurial = "s"
    return dimension["display"] + plurial


def get_readable_day(day):
    return {
        "m": "Lundi",
        "tu": "Mardi",
        "w": "Mercredi",
        "th": "Jeudi",
        "f": "Vendredi",
        "sa": "Samedi",
        "su": "Dimanche",
    }.get(day, "None")


def convert_to_list(dimension):
    if dimension is None:
        return []
    elif isinstance(dimension, Iterable):
        return list(dimension)
    else:
        return [dimension]


class Constraint:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        constraint_type=ConstraintType.UNDEFINED,
        instructors=None,
        slots=None,
        courses=None,
        periods=None,
        rooms=None,
        groups=None,
        days=None,
        departments=None,
        modules=None,
        apm=None,
        name=None,
    ):
        (
            instructors,
            slots,
            courses,
            periods,
            rooms,
            groups,
            days,
            departments,
            modules,
            apm,
        ) = self.handle_dimensions(
            instructors,
            slots,
            courses,
            periods,
            rooms,
            groups,
            days,
            departments,
            modules,
            apm,
        )
        self.name = name

        # self.id added with add_constraint
        self.constraint_type = constraint_type
        self.dimensions = {
            "instructors": {"display": "professeur", "value": instructors},
            "slots": {"display": "slot", "value": slots},
            "courses": {"display": "cours", "value": courses},
            "periods": {"display": "période", "value": periods},
            "rooms": {"display": "salle", "value": rooms},
            "groups": {
                "display": "groupe",
                "value": groups,
            },
            "days": {
                "display": "jour",
                "value": days,
            },
            "departments": {
                "display": "department",
                "value": departments,
            },
            "modules": {
                "display": "module",
                "value": modules,
            },
            "apm": {
                "display": "demi-journée",
                "value": apm,
            },
        }

    def handle_dimensions(
        self,
        instructors,
        slots,
        courses,
        periods,
        rooms,
        groups,
        days,
        departments,
        modules,
        apm,
    ):
        instructors = convert_to_list(instructors)
        periods = convert_to_list(periods)
        rooms = convert_to_list(rooms)
        groups = convert_to_list(groups)
        days = [get_readable_day(day) for day in convert_to_list(days)]
        departments = convert_to_list(departments)
        modules = convert_to_list(modules)
        apm = convert_to_list(apm)
        slots = convert_to_list(slots)
        courses = convert_to_list(courses)

        for slot in slots:
            day = get_readable_day(slot.get_day().weekday())
            if day not in days:
                days.append(day)
            for period in get_all_scheduling_periods(slot.department):
                if day in period.dates():
                    periods.append(period)

        for course in courses:
            if course.tutor not in instructors:
                instructors.append(course.tutor)
            for g in course.groups.all():
                if g not in groups:
                    groups.append(g)
            if course.module not in modules:
                modules.append(course.module)

        return (
            instructors,
            slots,
            courses,
            periods,
            rooms,
            groups,
            days,
            departments,
            modules,
            apm,
        )

    # generic method
    def get_summary_format(self):
        output = (
            "\tDes contraintes de type '%s' posent problème dans la résolution\n"
            % self.constraint_type.value
        )
        return output, []

    def get_csv_info(self):
        def f(x):
            if x == [] or x is None:
                return ""
            if isinstance(x, list):
                return " ".join([str(elem) for elem in x])
                # return ' '.join(';'.join(x))
            return str(x)

        res = [self.id, self.constraint_type.value]
        for dimension in self.dimensions:
            res.append(f(self.dimensions[dimension]["value"]))
        return tuple(res)

    def __str__(self):
        res = "(%s) La contrainte " % self.id
        if self.name:
            res += '"%s "' % self.name
        if self.constraint_type is not None:
            res += 'de type "%s" ; ' % self.constraint_type.value
        for dimension in self.dimensions.keys():
            if self.dimensions[dimension]["value"]:
                res += "pour %s %s ; " % (
                    sing_or_plural(self.dimensions[dimension]),
                    self.dimensions[dimension]["value"],
                )
        res += "doit être respectée."
        return res
