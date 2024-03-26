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

from TTapp.ilp_constraints.print_infaisibility import print_all


def inc(occurs_types, constraint_type):
    if constraint_type is not None:
        if constraint_type in occurs_types.keys():
            occurs_types[constraint_type]["occurences"] += 1
        else:
            occurs_types[constraint_type] = {"occurences": 1}


def inc_with_type(occurs_dimension, dimension, constraint_type):
    if dimension != []:
        for elt in dimension:
            if elt in occurs_dimension.keys():
                occurs_dimension[elt]["occurences"] += 1
                if constraint_type not in occurs_dimension[elt]["types"]:
                    occurs_dimension[elt]["types"].append(constraint_type)
            else:
                occurs_dimension[elt] = {"occurences": 1, "types": [constraint_type]}


class ConstraintManager:
    def __init__(self, threshold_type=60, threshold_attr=80):
        self.threshold_type = threshold_type  # % des types sont pris en compte
        self.threshold_attr = threshold_attr  # % des attributs sont pris en compte
        self.constraints = []
        self.infeasible_constraints = []
        self.occurs = None
        self.nb_constraints = 0

    def add_constraint(self, constraint):
        self.constraints.append(constraint)
        self.nb_constraints += 1

    def get_nb_constraints(self):
        return self.nb_constraints

    def get_constraints(self, id_constraints):
        return [self.constraints[id_constraint] for id_constraint in id_constraints]

    def parse_iis(self, iis_filename):
        with open(iis_filename, "r", encoding="utf-8") as f:
            data = f.read().split("Subject To\n")[1]
        constraints_declarations = data.split("Bounds")
        constraints_text = constraints_declarations[0]

        constraints_text = constraints_text.split(":")
        id_constraints = [constraints_text[0]]
        for i in range(1, len(constraints_text) - 1):
            id_constraints.append(constraints_text[i].split("=")[1].split("\n")[1][1:])

        def try_to_convert_to_number_else_none(string_number):
            try:
                return int(string_number)
            except ValueError:
                return None

        id_constraints = [
            try_to_convert_to_number_else_none(string_id)
            for string_id in id_constraints
            if try_to_convert_to_number_else_none(string_id) is not None
        ]
        return self.get_constraints(id_constraints)

    def get_occurs(self):
        occurs = {"types": {}}
        for dimension in self.infeasible_constraints[0].dimensions.keys():
            occurs[dimension] = {}

        for constraint in self.infeasible_constraints:
            constraint_type = constraint.constraint_type.value
            inc(occurs["types"], constraint_type)
            for dimension in constraint.dimensions.keys():
                inc_with_type(
                    occurs[dimension],
                    constraint.dimensions[dimension]["value"],
                    constraint_type,
                )

        for dimension in occurs:
            occurs[dimension] = sorted(
                occurs[dimension].items(),
                key=lambda elt: elt[1]["occurences"],
                reverse=True,
            )
        return occurs

    def set_index_courses(self):
        courses = list(self.occurs["courses"].keys())

        for index_course1, course1 in enumerate(courses):
            for index_course2 in range(index_course1 + 1, len(courses)):
                if course1.equals(courses[index_course2]):
                    course1.show_id = True
                    courses[index_course2].show_id = True

    def handle_reduced_result(
        self, iis_file_name, file_path, filename_suffixe, write_csv_file=False
    ):
        self.infeasible_constraints = self.parse_iis(iis_file_name)
        self.occurs = self.get_occurs()
        self.set_index_courses()
        print_all(
            self.infeasible_constraints,
            self.occurs,
            self.threshold_type,
            self.threshold_attr,
            file_path,
            filename_suffixe,
            write_csv_file=write_csv_file,
        )
