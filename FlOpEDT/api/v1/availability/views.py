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

from datetime import datetime, timedelta

from distutils.util import strtobool

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import django_filters.rest_framework as filters
from django.utils.decorators import method_decorator

from base.timing import date_to_flopday, Day

import base.models as bm
import people.models as pm

from api.v1.availability import serializers
from api.permissions import IsTutorOrReadOnly, IsAdminOrReadOnly, IsTutor
from api.shared.params import (
    week_param,
    year_param,
    user_id_param,
    dept_param,
    from_date_param,
    to_date_param,
    date_param,
    weekday_param,
)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            from_date_param(required=True),
            to_date_param(required=True),
            user_id_param(),
        ],
    ),
)
class UserDatedAvailabilityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]

    serializer_class = serializers.UserAvailabilitySerializer

    def get_queryset(self):
        from_date = datetime.fromisoformat(
            self.request.query_params.get("from_date")
        ).date()
        to_date = datetime.fromisoformat(
            self.request.query_params.get("to_date")
        ).date()

        if from_date > to_date:
            raise exceptions.NotAcceptable(
                '"from_date" parameter is later than "to_date" parameter'
            )

        user_id = self.request.query_params.get("user_id")
        if user_id is not None:
            user_id = int(user_id)

        # TODO V1-DB
        # ugly but will be removed
        ret = bm.UserPreference.objects.none()
        py_date = from_date
        cal = py_date.isocalendar()
        y, w, days = cal[0], cal[1], [Day.CHOICES[cal[2] - 1][0]]
        py_date += timedelta(days=1)
        while py_date <= to_date:
            cal = py_date.isocalendar()
            if cal[1] != w:
                if user_id is None:
                    ret |= bm.UserPreference.objects.filter(week__year=y, week__nb=w, day__in=days)   
                else:
                    ret |= bm.UserPreference.objects.filter(user__id=user_id, week__year=y, week__nb=w, day__in=days)
                y, w, days = cal[0], cal[1], [Day.CHOICES[cal[2] - 1][0]]
            else:
                days.append(Day.CHOICES[cal[2] - 1][0])
            py_date += timedelta(days=1)
        if user_id is None:
            ret |= bm.UserPreference.objects.filter(week__year=y, week__nb=w, day__in=days)   
        else:
            ret |= bm.UserPreference.objects.filter(user__id=user_id, week__year=y, week__nb=w, day__in=days)
        return ret
