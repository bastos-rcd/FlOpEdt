#!/usr/bin/env python3
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

#############
# PRINCIPLE #
#############
#
# This code loads and saves the description of a database ; in-memory
# the format is the one described in database_description_checker.py, and
# on-disk in a JSON format
#

import yaml


def database_description_save_yaml_file(filename, database):
    try:
        with open(filename, "w") as handle:
            handle.write(yaml.dump(database))
    except Exception as exc:
        print("Problem saving: ", exc)  # FIXME complain better


def database_description_load_yaml_file(filename):
    try:
        with open(filename, "r") as handle:
            result = yaml.load(handle.read(), Loader=yaml.FullLoader)
            return result
    except Exception as exc:
        print("Problem loading: ", exc)  # FIXME complain better
        return None
