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

import csv

from TTapp.ilp_constraints.constraint import Constraint


def print_all(
    constraints,
    occurs,
    threshold_type,
    threshold_attr,
    file_path,
    filename_suffixe,
    write_csv_file,
):
    print_brut_constraints(
        constraints, occurs, file_path, filename_suffixe, print_output=False
    )
    print_factorised_constraints(occurs, file_path, filename_suffixe, print_output=True)
    print_summary_from_types_with_threshold(
        constraints,
        occurs,
        threshold_type,
        threshold_attr,
        file_path,
        filename_suffixe,
        print_output=True,
    )
    if write_csv_file:
        write_csv(constraints, file_path, filename_suffixe)


def sort_constraints_by_type(constraints, occurs):
    order = list(occurs["types"].keys())
    constraints = sorted(
        constraints,
        key=lambda constraint: order.index(constraint.constraint_type.value),
    )
    return constraints


def print_brut_constraints(
    constraints, occurs, file_path, filename_suffixe, print_output=False
):
    constraints = sort_constraints_by_type(constraints, occurs)
    output = ""
    for constraint in constraints:
        output += str(constraint) + "\n"

    filename = f"{file_path}/constraints_all{filename_suffixe}.txt"
    write_file(filename, output, print_output=print_output)


def print_factorised_constraints(
    occurs, file_path, filename_suffixe, print_output=False
):
    output = (
        "\n Voici toutes les contraintes qui créent l'infaisabilité, factorisées :\n "
    )
    for dimension in occurs.keys():
        output += f"\n\n{dimension}:"
        for elt in occurs[dimension].keys():
            output += f"\n {elt} -> {occurs[dimension][elt]['types']}"
            if dimension != "types":
                output += f" ({', '.join(occurs[dimension][elt]['types'])})"
    filename = f"{file_path}/constraints_factorised{filename_suffixe}.txt"
    write_file(filename, output, print_output=print_output)


def get_most_important(dico, threshold, constraint_type=""):
    """
    Retourne une liste avec les X dimensions les plus occurentes,
    dont les occurences constituent threshold % du tout.
    """
    total = get_total_occurrences(dico, constraint_type)
    max_ = threshold * total / 100
    current = 0
    result = []
    for key in dico.keys():
        if current >= max_:
            break
        if constraint_type != "":
            if constraint_type in dico.get(key).get("types"):
                current += dico.get(key).get("occurences")
                result.append(key)
        else:
            current += dico.get(key).get("occurences")
            result.append(key)
    return result


def get_total_occurrences(dico, contraint_type):
    """
    Retourne la somme de toutes les occurences
    """
    total = 0
    for key in dico.keys():
        if contraint_type != "":
            if contraint_type in dico.get(key).get("types"):
                total += dico.get(key).get("occurences")
        else:
            total += dico.get(key).get("occurences")
    return total


def get_str_attr(dico, threshold, constraint_type):
    """
    Forme une liste indenté des X attributs les plus occurents,
    dont les occurences constituent threshold % du tout.
    """
    output = ""
    for attr in get_most_important(dico, threshold, constraint_type):
        output += f"\t\t{attr}\n"
    return output


def find_object_from_type(constraint_type, constraints):
    """
    Retourne une instance de la classe constraint correspondant au type donné,
    pour utiliser sa méthode get_summary_format().
    """
    for constraint in constraints:
        if constraint.constraint_type.value == constraint_type:
            return constraint
    return Constraint()


def print_summary_from_types_with_threshold(
    constraints,
    occurs,
    threshold_type,
    threshold_attr,
    file_path,
    filename_suffixe,
    print_output=False,
):
    filename = f"{file_path}/constraints_summary{filename_suffixe}.txt"
    output = "\n Voici les principales contraintes liées à l'infaisabilité :\n"
    write_file(filename, output)
    for constraint_type in get_most_important(occurs["types"], threshold_type):
        output, dimensions = find_object_from_type(
            constraint_type, constraints
        ).get_summary_format()
        fill = []
        for dimension in dimensions:
            fill.append(
                get_str_attr(occurs.get(dimension), threshold_attr, constraint_type)
            )
        output %= tuple(fill)
        write_file(filename, output, mode="a+", print_output=print_output)


def write_csv(constraints, file_path, filename_suffixe):
    filename = f"{file_path}/graph{filename_suffixe}.csv"
    print(f"writing {filename}...")
    with open(filename, "w+", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "ID",
                "Constraint type",
                "Instructors",
                "Slots",
                "Courses",
                "Week",
                "Rooms",
                "Group",
                "Days",
                "Departement",
                "Module",
            ]
        )
        for constraint in constraints:
            csv_info = constraint.get_csv_info()
            writer.writerow(csv_info)


def write_file(filename, output, print_output=True, mode="w+"):
    if mode == "w+":
        print(f"writing {filename}... \n")
    with open(filename, mode, encoding="utf-8") as file:
        file.write(output)
        file.write("\n")
    if print_output:
        print(f"\n{output}")
