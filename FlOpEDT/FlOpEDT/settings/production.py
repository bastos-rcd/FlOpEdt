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

from .base import *
import configparser, os

###############################
# Configuration File Parsing  #
###############################

SYSTEM_FLOP_CONFIG_FILE="/etc/flopedt/flopedt.ini"
STATIC_ROOT="/var/flopedt/static"
CACHE_DIRECTORY="/var/flopedt/cache"
TMP_DIRECTORY="/var/flopedt/tmp"

if os.environ.get('FLOP_CONFIG_FILE') is not None:
    if os.path.exists(os.environ.get('FLOP_CONFIG_FILE')):
        FLOP_CONFIG_FILE=os.environ.get('FLOP_CONFIG_FILE')
    else:
        print("Configuration file %s doesn't exist" % os.environ.get('FLOP_CONFIG_FILE'))
        sys.exit(1)
elif os.path.exists(SYSTEM_FLOP_CONFIG_FILE):
    FLOP_CONFIG_FILE=SYSTEM_FLOP_CONFIG_FILE
else:
    print("System configuration file %s doesn't exist" % SYSTEM_FLOP_CONFIG_FILE)
    sys.exit(1)

# Let's parse the configuration file
flop_config=configparser.ConfigParser()
flop_config.read(FLOP_CONFIG_FILE)

# Define static file configuration
try:
    if os.path.exists(flop_config['flopedt']['static_files']):
        STATIC_ROOT=flop_config['flopedt']['static_files']
except KeyError:
    pass

# Define cache file configuration
try:
    if os.path.exists(flop_config['flopedt']['cache_directory']):
        CACHE_DIRECTORY=flop_config['flopedt']['cache_directory']
except KeyError:
    pass

# Define cache file configuration
try:
    if os.path.exists(flop_config['flopedt']['tmp_directory']):
        TMP_DIRECTORY=flop_config['flopedt']['tmp_directory']
except KeyError:
    pass

# Define environment variable for GUROBI license
try:
    if os.path.exists(flop_config['gurobi']['license_file']):
        os.environ["GRB_LICENSE_FILE"]=flop_config['gurobi']['license_file']
    else:
        print("ATTENTION - Le fichier de licence GUROBI n'est pas présent. Le solveur GUROBI ne sera pas disponible")
except KeyError:
    pass

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
USE_TZ = False

SECRET_KEY = flop_config['flopedt']['secret_key']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': flop_config['database']['postgres_database'],
        'USER': flop_config['database']['postgres_username'],
        'HOST': flop_config['database']['postgres_hostname'],
        'PORT': int(flop_config['database']['postgres_port']),
        'PASSWORD': flop_config['database']['postgres_password'],
    }
}


LOGGING = {  
    'version': 1,  
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'base': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },        
        'configuration': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },        
        'django.db.backends': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        }
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': CACHE_DIRECTORY,
    }
}

CRONJOBS = [
    ('0 4 * * *', 'notifications.cron.backup_and_notify')
]

# YOU NEED TO SPECIFY ALLOWED_HOSTS FOR PRODUCTION ENVIRONMENT
ALLOWED_HOSTS = [ '127.0.0.1', 'localhost' ]
