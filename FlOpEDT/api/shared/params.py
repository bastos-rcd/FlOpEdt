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

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_yasg import openapi


def date_param(**kwargs):
    return OpenApiParameter(
        name="date",
        location=OpenApiParameter.QUERY,
        description="date",
        type=OpenApiTypes.DATE,
        **kwargs
    )


def weekday_param(**kwargs):
    return OpenApiParameter(
        name="weekday",
        location=OpenApiParameter.QUERY,
        description="weekday",
        type=OpenApiTypes.STR,
        **kwargs
    )


def from_date_param(**kwargs):
    return OpenApiParameter(
        "from_date",
        location=OpenApiParameter.QUERY,
        description="from date (included)",
        type=OpenApiTypes.DATE,
        **kwargs
    )


def to_date_param(**kwargs):
    return OpenApiParameter(
        "to_date",
        location=OpenApiParameter.QUERY,
        description="to date (included)",
        type=OpenApiTypes.DATE,
        **kwargs
    )


def week_param(**kwargs):
    return OpenApiParameter(
        "week_number",
        location=OpenApiParameter.QUERY,
        description="week number",
        type=OpenApiTypes.INT,
        **kwargs
    )


def year_param(**kwargs):
    return OpenApiParameter(
        "year",
        location=OpenApiParameter.QUERY,
        description="year",
        type=OpenApiTypes.INT,
        **kwargs
    )


def user_param(**kwargs):
    return OpenApiParameter(
        "user",
        location=OpenApiParameter.QUERY,
        description="username",
        type=OpenApiTypes.STR,
        **kwargs
    )


def user_id_param(**kwargs):
    return OpenApiParameter(
        "user_id",
        location=OpenApiParameter.QUERY,
        description="user id",
        type=OpenApiTypes.INT,
        **kwargs
    )


def room_id_param(**kwargs):
    return OpenApiParameter(
        "room_id",
        location=OpenApiParameter.QUERY,
        description="room id",
        type=OpenApiTypes.INT,
        **kwargs
    )


def tutor_param(**kwargs):
    return OpenApiParameter(
        "tutor",
        location=OpenApiParameter.QUERY,
        description="tutor username",
        type=OpenApiTypes.STR,
        **kwargs
    )


def tutor_id_param(**kwargs):
    return OpenApiParameter(
        "tutor_id",
        location=OpenApiParameter.QUERY,
        description="tutor id",
        type=OpenApiTypes.INT,
        **kwargs
    )


def dept_param(**kwargs):
    return OpenApiParameter(
        "dept",
        location=OpenApiParameter.QUERY,
        description="department abbreviation",
        type=OpenApiTypes.STR,
        **kwargs
    )


def dept_id_param(**kwargs):
    return OpenApiParameter(
        "dept_id",
        location=OpenApiParameter.QUERY,
        description="department id",
        type=OpenApiTypes.INT,
        **kwargs
    )


def work_copy_param(**kwargs):
    return OpenApiParameter(
        "work_copy",
        location=OpenApiParameter.QUERY,
        description="N° of work copy (default: 0)",
        type=OpenApiTypes.INT,
        **kwargs
    )


def group_param(**kwargs):
    return OpenApiParameter(
        "group",
        location=OpenApiParameter.QUERY,
        description="Group name",
        type=OpenApiTypes.STR,
        **kwargs
    )


def struct_group_param(**kwargs):
    return OpenApiParameter(
        "struct_group",
        location=OpenApiParameter.QUERY,
        description="Structural group name",
        type=OpenApiTypes.STR,
        **kwargs
    )


def struct_group_id_param(**kwargs):
    return OpenApiParameter(
        "struct_group_id",
        location=OpenApiParameter.QUERY,
        description="Structural group id",
        type=OpenApiTypes.INT,
        **kwargs
    )


def train_prog_param(**kwargs):
    return OpenApiParameter(
        "train_prog",
        location=OpenApiParameter.QUERY,
        description="Training programme abbreviation",
        type=OpenApiTypes.STR,
        **kwargs
    )


def train_prog_id_param(**kwargs):
    return OpenApiParameter(
        "train_prog_id",
        location=OpenApiParameter.QUERY,
        description="Training programme id",
        type=OpenApiTypes.INT,
        **kwargs
    )


def lineage_param(**kwargs):
    return OpenApiParameter(
        "lineage",
        location=OpenApiParameter.QUERY,
        description="includes parent groups (default: false)",
        type=OpenApiTypes.BOOL,
        **kwargs
    )


def and_transversal_param(**kwargs):
    return OpenApiParameter(
        "and_transversal",
        location=OpenApiParameter.QUERY,
        description="include related transversal groups (default: true)",
        type=OpenApiTypes.BOOL,
        **kwargs
    )
