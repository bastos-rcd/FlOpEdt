# coding: utf-8
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

import json
import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from numpy import diag, eye
from pyclustering.gcolor.dsatur import dsatur

from base.models import Course, Module, TrainingProgramme
from base.weeks import week_list
from displayweb.models import ModuleDisplay, TutorDisplay
from people.models import Tutor


def assign_tutor_color(department=None):
    all_tutors = Tutor.objects.all()
    if department is not None:
        all_tutors = all_tutors.filter(departments=department)
    color_set = get_color_set(
        os.path.join(settings.BASE_DIR, "misc", "colors.json"), all_tutors.count()
    )
    for tut, col in zip(all_tutors, color_set):
        td, _ = TutorDisplay.objects.get_or_create(tutor=tut)
        td.color_bg = col
        td.color_txt = compute_luminance(col)
        td.save()


def assign_module_color(
    department, overwrite=True, diff_across_train_prog=False, with_graph_matrices=False
):
    """
    Assigns a color to each module
    :param department department
    :param overwrite: if overwrite, overwrites all preexisting colors,
    otherwise does not touch the existing colors, but considers that they do not
    belong to the colors chosen in colors.json
    :param diff_across_train_prog: if diff_across_train_prog, it is required
    that two simultaneous modules should wear different colors even if they
    belong to different training programmes
    :return:
    """
    if department is None:
        raise ValueError("Please provide a department")
    if diff_across_train_prog:
        if with_graph_matrices:
            keys, mat = with_graph_matrices(None, department)
        else:
            keys, mat = (
                list(Module.objects.filter(train_prog__department=department)),
                None,
            )
        optim_and_save(keys, mat, overwrite)
    else:
        for train_prog in TrainingProgramme.objects.filter(department=department):
            print(train_prog)
            if with_graph_matrices:
                keys, mat = with_graph_matrices(train_prog, department)
            else:
                keys, mat = list(Module.objects.filter(train_prog=train_prog)), None
            optim_and_save(keys, mat, overwrite)


def optim_and_save(keys, mat, overwrite):
    if mat is not None:
        if len(mat) == 0:
            print("No course in this training programme!")
            return
        opti = dsatur(mat)
        opti.process()
        color_indices = opti.get_colors()
        print(color_indices, max(color_indices))
        color_set = get_color_set(
            os.path.join(settings.BASE_DIR, "misc", "colors.json"), max(color_indices)
        )
    else:
        color_set = [
            "#208eb7",
            "#8fba06",
            "#961d6b",
            "#63e118",
            "#ef6ade",
            "#207a3f",
            "#fe16f4",
            "#83c989",
            "#af3014",
            "#20d8fd",
            "#6a3747",
            "#1cf1a3",
            "#1932bf",
            "#efd453",
            "#5310f0",
            "#fca552",
            "#274c56",
            "#ddc0bd",
            "#2d68c7",
            "#9a5c0d",
            "#c098fd",
            "#474a09",
            "#fb899b",
        ]
    for mi, module in enumerate(keys):
        if mat is not None:
            cbg = color_set[color_indices[mi] - 1]
        else:
            cbg = color_set[mi % len(color_set)]
        try:
            mod_disp = ModuleDisplay.objects.get(module=module)
            if overwrite:
                mod_disp.color_bg = cbg
                mod_disp.color_txt = compute_luminance(cbg)
                mod_disp.save()
        except ObjectDoesNotExist:
            mod_disp = ModuleDisplay(
                module=module, color_bg=cbg, color_txt=compute_luminance(cbg)
            )
            mod_disp.save()


def build_graph_matrices(train_prog, department=None):
    if train_prog is None and department is None:
        raise ValueError("You need to provide at least a department")
    if train_prog is None:
        keys = list(Module.objects.filter(train_prog__department=department))
    else:
        keys = list(Module.objects.filter(train_prog=train_prog))
    mat = eye(len(keys))
    wl = week_list()

    for mi, module_i in enumerate(keys):
        for mj in range(mi + 1, len(keys)):
            for wy in wl:
                if (
                    Course.objects.filter(
                        week__nb=wy["week"],
                        week__year=wy["year"],
                        module__in=[module_i, keys[mj]],
                    )
                    .distinct("module")
                    .count()
                    == 2
                ):
                    mat[(mi, mj)] = 1
                    break
    mat += mat.T - diag(mat.diagonal())
    print("Conflict matrix:")
    print(mat)
    return keys, mat


def get_color_set(filename, target_nb_colors):
    """
    Builds a color set from a json file which contains a list of
    {"tot": number_of_colors, "colors": list of colors maximizing the
    perceptual distance within the list}, cf. http://vrl.cs.brown.edu/color.
    :param filename: the colors.json
    :param target_nb_colors: minimum number of colors
    :return: a set of colors, not smaller than needed
    """
    color_set = ["red"]
    with open(filename, encoding="utf-8") as json_data:
        initial_colors = json.load(json_data)

        # find smallest set, bigger than needed
        # otherwise just the biggest
        for init_color_set in initial_colors:
            if len(init_color_set["colors"]) > len(color_set):
                if len(color_set) < target_nb_colors:
                    color_set = init_color_set["colors"]
            else:
                if len(init_color_set["colors"]) >= target_nb_colors:
                    color_set = init_color_set["colors"]

        print(color_set)

        # extend the color set if needed
        if len(color_set) < target_nb_colors:
            sliced = color_set[:]
            add_factor = target_nb_colors // len(color_set)
            for _ in range(add_factor):
                color_set += sliced
            # shrink the color set if needed
            if len(color_set) > target_nb_colors:
                color_set = color_set[len(color_set) - target_nb_colors :]

    return color_set


def compute_luminance(col):
    hexa = col[1:]
    perceived_luminance = (
        0.299 * int("0x" + hexa[0:2], 16)
        + 0.587 * int("0x" + hexa[2:4], 16)
        + 0.114 * int("0x" + hexa[4:6], 16)
    )
    if perceived_luminance < 127.5:
        return "#FFFFFF"
    return "#000000"
