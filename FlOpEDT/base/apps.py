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

from django.apps import AppConfig
import os

class BaseConfig(AppConfig):
    name = 'base'

    def ready(self):
        import base.signals
        from django.conf import settings as ds

        # STARTUP code
        # Create directory for serving static content in production
        if not os.path.exists(ds.STATIC_ROOT):
        
            # Directory doesn't exist let's create it
            print("Let's create %s" % ds.STATIC_ROOT)
            os.makedirs(ds.STATIC_ROOT,exist_ok=True)
        
        # Create directory for django cache
        if not os.path.exists(ds.CACHE_DIRECTORY):
        
            # Directory doesn't exist let's create it
            print("Let's create %s" % ds.CACHE_DIRECTORY)
            os.makedirs(ds.CACHE_DIRECTORY,exist_ok=True)
        
        # Create tmp directory used for solver resolution
        if not os.path.exists(ds.TMP_DIRECTORY):
        
            # Directory doesn't exist let's create it
            print("Let's create %s" % ds.TMP_DIRECTORY)
            os.makedirs(ds.TMP_DIRECTORY,exist_ok=True)
        
        # Let's create the missing directories
        os.makedirs(os.path.join(ds.TMP_DIRECTORY,"misc/logs/iis"),exist_ok=True)
