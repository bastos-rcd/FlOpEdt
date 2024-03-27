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

from django.apps import AppConfig
from django.conf import settings as ds


class BaseConfig(AppConfig):
    name = "base"

    def ready(self):

        # STARTUP code
        # Create directory for serving static content in production
        if not os.path.exists(ds.STATIC_ROOT):
            # Directory doesn't exist let's create it
            print(f"Let's create {ds.STATIC_ROOT}")
            os.makedirs(ds.STATIC_ROOT, exist_ok=True)

        # Create directory for serving media content in production
        if not os.path.exists(ds.MEDIA_ROOT):
            # Directory doesn't exist let's create it
            print(f"Let's create {ds.MEDIA_ROOT}")
            os.makedirs(ds.MEDIA_ROOT, exist_ok=True)

        # Create directory for django cache
        if not os.path.exists(ds.CACHE_DIRECTORY):
            # Directory doesn't exist let's create it
            print(f"Let's create {ds.CACHE_DIRECTORY}")
            os.makedirs(ds.CACHE_DIRECTORY, exist_ok=True)

        # Create tmp directory used for solver resolution
        if not os.path.exists(ds.TMP_DIRECTORY):
            # Directory doesn't exist let's create it
            print(f"Let's create {ds.TMP_DIRECTORY}")
            os.makedirs(ds.TMP_DIRECTORY, exist_ok=True)

        # Create storage directory
        if not os.path.exists(ds.STORAGE_DIRECTORY):
            # Directory doesn't exist let's create it
            print(f"Let's create {ds.STORAGE_DIRECTORY}")
            os.makedirs(ds.STORAGE_DIRECTORY, exist_ok=True)

        # Let's create the missing subdirectories
        directories_to_create = [
            os.path.join(ds.TMP_DIRECTORY, "misc/logs/iis"),
            os.path.join(ds.TMP_DIRECTORY, "misc/logs/solutions"),
            os.path.join(ds.TMP_DIRECTORY, "misc/logs/gurobi"),
            os.path.join(ds.STORAGE_DIRECTORY, "configuration"),
        ]
        for cur_directory in directories_to_create:
            if not os.path.exists(cur_directory):
                # Directory doesn't exist let's create it
                print(f"Let's create {cur_directory}")
                os.makedirs(cur_directory, exist_ok=True)
