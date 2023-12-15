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

from drf_yasg import openapi


def date_param(**kwargs):
    return openapi.Parameter(
        "date",
        openapi.IN_QUERY,
        description="date",
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        **kwargs
    )


def weekday_param(**kwargs):
    return openapi.Parameter('weekday',
                             openapi.IN_QUERY,
                             description="weekday",
                             type=openapi.TYPE_STRING,
                             **kwargs)


def from_date_param(**kwargs):
    return openapi.Parameter("from_date",
                             openapi.IN_QUERY,
                             description="from date",
                             type=openapi.FORMAT_DATE,
                             **kwargs)


def to_date_param(**kwargs):
    return openapi.Parameter("to_date",
                             openapi.IN_QUERY,
                             description="to date",
                             type=openapi.FORMAT_DATE,
                             **kwargs)


def week_param(**kwargs):
    return openapi.Parameter('week_number',
                             openapi.IN_QUERY,
                             description="week number",
                             type=openapi.TYPE_INTEGER,
                             **kwargs)


def year_param(**kwargs):
    return openapi.Parameter('year',
                             openapi.IN_QUERY,
                             description="year",
                             type=openapi.TYPE_INTEGER,
                             **kwargs)


def user_param(**kwargs):
    return openapi.Parameter('user',
                             openapi.IN_QUERY,
                             description="username",
                             type=openapi.TYPE_STRING,
                             **kwargs)


def tutor_param(**kwargs):
    return openapi.Parameter('tutor_name',
                             openapi.IN_QUERY,
                             description="tutor username",
                             type=openapi.TYPE_STRING,
                             **kwargs)


def dept_param(**kwargs):
    return openapi.Parameter('dept',
                             openapi.IN_QUERY,
                             description="department abbreviation",
                             type=openapi.TYPE_STRING,
                             **kwargs)


def work_copy_param(**kwargs):
    return openapi.Parameter('work_copy',
                             openapi.IN_QUERY,
                             description="N° of work copy (default: 0)",
                             type=openapi.TYPE_INTEGER,
                             **kwargs)


def group_param(**kwargs):
    return openapi.Parameter('group',
                             openapi.IN_QUERY,
                             description="Group name",
                             type=openapi.TYPE_STRING,
                             **kwargs)


def train_prog_param(**kwargs):
    return openapi.Parameter('train_prog',
                             openapi.IN_QUERY,
                             description="Training programme abbreviation",
                             type=openapi.TYPE_STRING,
                             **kwargs)


def lineage_param(**kwargs):
    return openapi.Parameter('lineage',
                             openapi.IN_QUERY,
                             description="includes parent groups (default: false)",
                             type=openapi.TYPE_BOOLEAN,
                             **kwargs)
