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

"""
Django settings for FlOpEDT project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import configparser
import os
import sys

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#
# Application definition
#

INSTALLED_APPS = [
    "channels",
    "apps.FlOpEDTAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "import_export",
    "colorfield",
    "flopeditor",
    "rest_framework",
    "django_filters",
    "base",
    "MyFlOp",
    "TTapp",
    "quote",
    "people",
    "solve_board",
    "flop_ics",
    "displayweb",
    "configuration",
    "easter_egg",
    #    'importation'
    "api",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "drf_spectacular",
    "corsheaders",
    "cstmanager",
    "notifications",
    "django_crontab",
    "roomreservation",
    "acme_challenge",
    "rules.apps.AutodiscoverRulesConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.EdtContextMiddleware",
]

ROOT_URLCONF = "FlOpEDT.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.edt_context",
            ],
        },
    },
]

WSGI_APPLICATION = "FlOpEDT.wsgi.application"
ASGI_APPLICATION = "FlOpEDT.routing.application"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "flop",
    }
}

CACHE_COUNT_TIMEOUT = 24 * 3600
CACHE_INVALIDATE_ON_CREATE = "whole-model"
CACHE_MACHINE_USE_REDIS = True
REDIS_BACKEND = "redis://127.0.0.1:6379/1"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False
CSRF_USE_SESSION = True
AUTH_USER_MODEL = "people.User"

# Available languages
LANGUAGES = [
    ("fr", _("French")),
    ("en", _("English")),
    ("es", _("Spanish")),
    ("ar", _("Arabic")),
    ("eu", _("Basque")),
    ("br", _("Breton")),
    ("ca", _("Catalan")),
    ("co", _("Corsican")),
    ("da", _("Danish")),
    ("de", _("German")),
    ("nl", _("Dutch")),
    ("el", _("Greek")),
    ("it", _("Italian")),
    ("la", _("Latin")),
    ("no", _("Norwegian")),
    ("pl", _("Polish")),
    ("pt", _("Portuguese")),
    ("sv", _("Swedish")),
    ("zh", _("Chinese")),
    ("sf", _("Smurf")),
]

# Folder which contains traduction files
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

#
# ASSETS Settings
#

# Url used by static files in templates
STATIC_URL = "/static/"

# Folder used to store collected static files
STATIC_ROOT = os.path.join(BASE_DIR, "var/static")

# Folders used to find some additional static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"

#
# FLOPEDT Settings
#

CUSTOM_CONSTRAINTS_PATH = "MyFlOp.custom_constraints"

if "ADMINS" in os.environ:
    ADMINS = [tuple(admin.split(",")) for admin in os.environ.get("ADMINS").split(" ")]
    MANAGERS = ADMINS

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework_csv.renderers.CSVRenderer",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API flop",
    "DESCRIPTION": "Communiquer avec flop!",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Use the host domain and port instead of Django's
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# LOG IN-AND-OUT
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/"
TEMPLATE_DIRS = (BASE_DIR + "/templates/",)

SHELL_PLUS_MODEL_IMPORTS_RESOLVER = (
    "django_extensions.collision_resolvers.AppLabelSuffixCR"
)
SHELL_PLUS_IMPORTS = ("import datetime as dt",)

CORS_ALLOW_ALL_ORIGINS = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

###############################
# Configuration File Parsing  #
###############################

SYSTEM_FLOP_CONFIG_FILE = "/etc/flopedt/flopedt.ini"
STATIC_ROOT = "/var/flopedt/static"
CACHE_DIRECTORY = "/var/flopedt/cache"
TMP_DIRECTORY = "/var/flopedt/tmp"
STORAGE_DIRECTORY = "/var/flopedt/storage"

if os.environ.get("FLOP_CONFIG_FILE") is not None:
    if os.path.exists(os.environ.get("FLOP_CONFIG_FILE")):
        FLOP_CONFIG_FILE = os.environ.get("FLOP_CONFIG_FILE")
    else:
        print(
            "Configuration file %s doesn't exist" % os.environ.get("FLOP_CONFIG_FILE")
        )
        sys.exit(1)
elif os.path.exists(SYSTEM_FLOP_CONFIG_FILE):
    FLOP_CONFIG_FILE = SYSTEM_FLOP_CONFIG_FILE
else:
    print("System configuration file %s doesn't exist" % SYSTEM_FLOP_CONFIG_FILE)
    sys.exit(1)

# Let's parse the configuration file
flop_config = configparser.ConfigParser()
flop_config.read(FLOP_CONFIG_FILE)

# Define static file configuration
try:
    # The directory is available let's set the configuration parameter
    STATIC_ROOT = flop_config["flopedt"]["static_directory"]
except KeyError:
    print(
        "Static directory not defined in configuration file. Let's fall back to %s"
        % STATIC_ROOT
    )
    pass

# Define cache directory configuration
try:
    # The directory is available let's set the configuration parameter
    CACHE_DIRECTORY = flop_config["flopedt"]["cache_directory"]
except KeyError:
    print(
        "Cache directory not defined in configuration file. Let's fall back to %s"
        % CACHE_DIRECTORY
    )
    pass

# Define tmp directory configuration
try:
    # The directory is available let's set the configuration parameter
    TMP_DIRECTORY = flop_config["flopedt"]["tmp_directory"]
except KeyError:
    print(
        "Temp directory not defined in configuration file. Let's fall back to %s"
        % TMP_DIRECTORY
    )
    pass

# Define storage configuration
try:
    # The directory is available let's set the configuration parameter
    STORAGE_DIRECTORY = flop_config["flopedt"]["storage_directory"]
except KeyError:
    print(
        "Storage directory not defined in configuration file. Let's fall back to %s"
        % STORAGE_DIRECTORY
    )
    pass

# Define environment variable for GUROBI license
try:
    if os.path.exists(flop_config["gurobi"]["license_file"]):
        os.environ["GRB_LICENSE_FILE"] = flop_config["gurobi"]["license_file"]
    else:
        print(
            "WARNING - Declared GUROBI license file is not readable. GUROBI solver won't be available"
        )
except KeyError:
    print("WARNING - GUROBI License is not declared. GUROBI solver won't be available")
    pass

# Define subdirs and other dirs
MEDIA_ROOT = TMP_DIRECTORY
CONF_XLS_DIR = os.path.join(STORAGE_DIRECTORY, "configuration")

# Secret Key
try:
    if flop_config["flopedt"]["secret_key"] is None:
        print("ERROR - Secret key is empty. The application won't start")
        sys.exit(1)
    else:
        SECRET_KEY = flop_config["flopedt"]["secret_key"]
except KeyError:
    print("ERROR - Secret key not defined. The application won't start")
    sys.exit(1)

# Import REDIS parameters
try:
    REDIS_SERVER = flop_config["redis"]["redis_host"]
except KeyError:
    print("REDIS HOST not configured - The constraint generator won't work")
    sys.exit(1)

try:
    REDIS_PORT = flop_config["redis"]["redis_port"]
except KeyError:
    print("REDIS PORT not configured - The constraint generator won't work")
    sys.exit(1)

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": flop_config["database"]["postgres_database"],
        "USER": flop_config["database"]["postgres_username"],
        "HOST": flop_config["database"]["postgres_hostname"],
        "PORT": int(flop_config["database"]["postgres_port"]),
        "PASSWORD": flop_config["database"]["postgres_password"],
    }
}

# REDIS configuration (For Solver messages)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_SERVER, REDIS_PORT)],
        },
    },
}

# Django CACHE
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": CACHE_DIRECTORY,
    }
}

# EMAIL SETTINGS
EMAIL_SUBJECT_PREFIX = "[flop!EDT] "
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

try:
    EMAIL_HOST = flop_config["email"]["email_host"]
except KeyError:
    print("WARNING - email_host is not configured. Mail sending won't work")
try:
    EMAIL_PORT = flop_config["email"]["email_port"]
except KeyError:
    print("WARNING - email_port is not configured. Mail sending won't work")
try:
    EMAIL_USE_SSL = bool(flop_config["email"]["email_use_ssl"])
except KeyError:
    print("WARNING - email_use_ssl is not configured. SSL Email sending disabled")
    EMAIL_USE_SSL = False
try:
    EMAIL_HOST_USER = flop_config["email"]["email_user"]
except KeyError:
    print(
        "WARNING - email_user is not configured. Mail sending won't work if your email server requires authentication."
    )
try:
    EMAIL_HOST_PASSWORD = flop_config["email"]["email_password"]
except KeyError:
    print(
        "WARNING - email_password is not configured. Mail sending won't work if your email server requires authentication."
    )
try:
    DEFAULT_FROM_EMAIL = flop_config["email"]["email_sender"]
except KeyError:
    print(
        "WARNING - email_sender is not configured. Mail sending won't work if sender email is not defined. Default value is webmaster@localhost"
    )

# Logging settings
try:
    if flop_config["flopedt"]["log_level"] in [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]:
        CONFIG_LOG_LEVEL = flop_config["flopedt"]["log_level"]
    else:
        print(
            "ERROR - Uncorrect log level defined in configuration file. Accepted values are : DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )
        sys.exit(1)
except KeyError:
    # No log_level configured => Let's fall back to INFO
    CONFIG_LOG_LEVEL = "INFO"

# YOU NEED TO SPECIFY ALLOWED_HOSTS FOR PRODUCTION ENVIRONMENT
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Import additional ALLOWED_HOSTS from configuration file
try:
    new_allowed_hosts = flop_config["flopedt"]["allowed_hosts"].split(",")
    ALLOWED_HOSTS = ALLOWED_HOSTS + new_allowed_hosts
except KeyError:
    # No additionnal hosts ==> Continue
    pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": CONFIG_LOG_LEVEL,
            "propagate": False,
        },
    },
}

# Configure django-crontab to use flop_admin as manage script when it exists
CRONTAB_DJANGO_MANAGE_PATH = sys.argv[0]

###############################
# Configuration File Parsing  #
###############################

SYSTEM_FLOP_CONFIG_FILE = "/etc/flopedt/flopedt.ini"
STATIC_ROOT = "/var/flopedt/static"
CACHE_DIRECTORY = "/var/flopedt/cache"
TMP_DIRECTORY = "/var/flopedt/tmp"
STORAGE_DIRECTORY = "/var/flopedt/storage"

if os.environ.get("FLOP_CONFIG_FILE") is not None:
    if os.path.exists(os.environ.get("FLOP_CONFIG_FILE")):
        FLOP_CONFIG_FILE = os.environ.get("FLOP_CONFIG_FILE")
    else:
        print(
            "Configuration file %s doesn't exist" % os.environ.get("FLOP_CONFIG_FILE")
        )
        sys.exit(1)
elif os.path.exists(SYSTEM_FLOP_CONFIG_FILE):
    FLOP_CONFIG_FILE = SYSTEM_FLOP_CONFIG_FILE
else:
    print("System configuration file %s doesn't exist" % SYSTEM_FLOP_CONFIG_FILE)
    sys.exit(1)

# Let's parse the configuration file
flop_config = configparser.ConfigParser()
flop_config.read(FLOP_CONFIG_FILE)

# Define static file configuration
try:
    # The directory is available let's set the configuration parameter
    STATIC_ROOT = flop_config["flopedt"]["static_directory"]
except KeyError:
    print(
        "Static directory not defined in configuration file. Let's fall back to %s"
        % STATIC_ROOT
    )
    pass

# Define cache directory configuration
try:
    # The directory is available let's set the configuration parameter
    CACHE_DIRECTORY = flop_config["flopedt"]["cache_directory"]
except KeyError:
    print(
        "Cache directory not defined in configuration file. Let's fall back to %s"
        % CACHE_DIRECTORY
    )
    pass

# Define tmp directory configuration
try:
    # The directory is available let's set the configuration parameter
    TMP_DIRECTORY = flop_config["flopedt"]["tmp_directory"]
except KeyError:
    print(
        "Temp directory not defined in configuration file. Let's fall back to %s"
        % TMP_DIRECTORY
    )
    pass

# Define storage configuration
try:
    # The directory is available let's set the configuration parameter
    STORAGE_DIRECTORY = flop_config["flopedt"]["storage_directory"]
except KeyError:
    print(
        "Storage directory not defined in configuration file. Let's fall back to %s"
        % STORAGE_DIRECTORY
    )
    pass

# Define environment variable for GUROBI license
try:
    if os.path.exists(flop_config["gurobi"]["license_file"]):
        os.environ["GRB_LICENSE_FILE"] = flop_config["gurobi"]["license_file"]
    else:
        print(
            "WARNING - Declared GUROBI license file is not readable. GUROBI solver won't be available"
        )
except KeyError:
    print("WARNING - GUROBI License is not declared. GUROBI solver won't be available")
    pass

# Define subdirs and other dirs
MEDIA_ROOT = TMP_DIRECTORY
CONF_XLS_DIR = os.path.join(STORAGE_DIRECTORY, "configuration")

# Secret Key
try:
    if flop_config["flopedt"]["secret_key"] is None:
        print("ERROR - Secret key is empty. The application won't start")
        sys.exit(1)
    else:
        SECRET_KEY = flop_config["flopedt"]["secret_key"]
except KeyError:
    print("ERROR - Secret key not defined. The application won't start")
    sys.exit(1)

# Import REDIS parameters
try:
    REDIS_SERVER = flop_config["redis"]["redis_host"]
except KeyError:
    print("REDIS HOST not configured - The constraint generator won't work")
    sys.exit(1)

try:
    REDIS_PORT = flop_config["redis"]["redis_port"]
except KeyError:
    print("REDIS PORT not configured - The constraint generator won't work")
    sys.exit(1)

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": flop_config["database"]["postgres_database"],
        "USER": flop_config["database"]["postgres_username"],
        "HOST": flop_config["database"]["postgres_hostname"],
        "PORT": int(flop_config["database"]["postgres_port"]),
        "PASSWORD": flop_config["database"]["postgres_password"],
    }
}

# REDIS configuration (For Solver messages)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_SERVER, REDIS_PORT)],
        },
    },
}

# Django CACHE
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": CACHE_DIRECTORY,
    }
}

# EMAIL SETTINGS
EMAIL_SUBJECT_PREFIX = "[flop!EDT] "
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

try:
    EMAIL_HOST = flop_config["email"]["email_host"]
except KeyError:
    print("WARNING - email_host is not configured. Mail sending won't work")
try:
    EMAIL_PORT = flop_config["email"]["email_port"]
except KeyError:
    print("WARNING - email_port is not configured. Mail sending won't work")
try:
    EMAIL_USE_SSL = bool(flop_config["email"]["email_use_ssl"])
except KeyError:
    print("WARNING - email_use_ssl is not configured. SSL Email sending disabled")
    EMAIL_USE_SSL = False
try:
    EMAIL_HOST_USER = flop_config["email"]["email_user"]
except KeyError:
    print(
        "WARNING - email_user is not configured. Mail sending won't work if your email server requires authentication."
    )
try:
    EMAIL_HOST_PASSWORD = flop_config["email"]["email_password"]
except KeyError:
    print(
        "WARNING - email_password is not configured. Mail sending won't work if your email server requires authentication."
    )
try:
    DEFAULT_FROM_EMAIL = flop_config["email"]["email_sender"]
except KeyError:
    print(
        "WARNING - email_sender is not configured. Mail sending won't work if sender email is not defined. Default value is webmaster@localhost"
    )

# Logging settings
try:
    if flop_config["flopedt"]["log_level"] in [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]:
        CONFIG_LOG_LEVEL = flop_config["flopedt"]["log_level"]
    else:
        print(
            "ERROR - Uncorrect log level defined in configuration file. Accepted values are : DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )
        sys.exit(1)
except KeyError:
    # No log_level configured => Let's fall back to INFO
    CONFIG_LOG_LEVEL = "INFO"

# YOU NEED TO SPECIFY ALLOWED_HOSTS FOR PRODUCTION ENVIRONMENT
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Import additional ALLOWED_HOSTS from configuration file
try:
    new_allowed_hosts = flop_config["flopedt"]["allowed_hosts"].split(",")
    ALLOWED_HOSTS = ALLOWED_HOSTS + new_allowed_hosts
except KeyError:
    # No additionnal hosts ==> Continue
    pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": CONFIG_LOG_LEVEL,
            "propagate": False,
        },
    },
}


# Specific cronjob
# CRONJOBS = [("0 4 * * *", "notifications.cron.backup_and_notify")]
try:
    CRONJOBS = [
        (
            cron_time,
            cron_command.replace(" ", "").split(",")[0],
            cron_command.replace(" ", "").split(",")[1:],
        )
        for cron_time, cron_command in flop_config["cronjobs"].items()
    ]
except KeyError:
    print("WARNING - no CRON jobs hence no backup is configured")
    CRONJOBS = []


AUTHENTICATION_BACKENDS = (
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
    #    'FlOpEDT.backend.DjangoRulesBackend',
)

# from rules.permissions import ObjectPermissionBackend
# from rules.contrib.rest_framework import AutoPermissionViewSetMixin
# from django.contrib.auth.backends import ModelBackend
