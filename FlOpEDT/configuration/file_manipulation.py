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

import os

from django.conf import settings


def upload_file(file, file_name):
    """
    Save the file at the path in the folder MEDIA.
    :param file: the file
    :param path_name: the target's path
    :return: the path of the saved file
    """
    path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(path, "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return path


def check_ext_file(file, exts):
    """
    Check the matching of extension file.
    :param file: file name
    :param exts: extensions to match against
    :return:
    """
    for ext in exts:
        if file.name.endswith(ext):
            return True
    return False
