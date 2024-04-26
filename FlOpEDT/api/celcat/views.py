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

import datetime as dt

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, APIException

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.utils.decorators import method_decorator
from django.db.models import Q
from base.models import ScheduledCourse, Department, TrainingProgramme

from api.permissions import IsTutorOrReadOnly
from api.shared.params import dept_param
from api.celcat.serializers import CelcatExportSerializer


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            dept_param(required=True),
            openapi.Parameter(
                "from",
                openapi.IN_QUERY,
                description="initial date",
                type=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                "to",
                openapi.IN_QUERY,
                description="final date",
                type=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                "train_prog",
                openapi.IN_QUERY,
                description="training program abbreviation",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ]
    ),
)
class CelcatExportViewSet(viewsets.ViewSet):
    """
    Creation of a Celcat export file
    """

    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):

        param_exception = NotAcceptable(detail="Usage : ?from=YYYY-MM-DD&to=YYYY-MM-DD")

        wanted_param = ["from", "to"]
        supp_filters = {}

        # check that all parameters are given
        for param in wanted_param:
            if param not in request.GET:
                raise param_exception

        dept = self.request.query_params.get("dept", None)
        if dept is not None:
            try:
                dept = Department.objects.get(abbrev=dept)
            except Department.DoesNotExist as exc:
                raise APIException(detail="Unknown department") from exc

        # clean dates
        from_date = dt.date.fromisoformat(self.request.query_params.get("from"))
        to_date = dt.date.fromisoformat(self.request.query_params.get("to"))

        # clean training programme
        train_prog = self.request.query_params.get("train_prog", None)
        if train_prog is not None:
            try:
                train_prog = TrainingProgramme.objects.get(
                    department=dept, abbrev=train_prog
                )
                supp_filters["course__module__train_prog"] = train_prog
            except TrainingProgramme.DoesNotExist as exc:
                raise APIException(detail="Unknown training programme") from exc

        considered_scheduled_courses = ScheduledCourse.objects.select_related(
            "course__module__train_prog", "course__type", "room", "tutor"
        ).filter(
            date__gte=from_date,
            date__lte=to_date,
            course__type__department=dept,
            work_copy=0,
            **supp_filters,
        )

        to_serialize_list = []
        for sc in considered_scheduled_courses:
            to_serialize_list += [
                sc,
                sc.course.module,
                sc.course.groups.first(),
                sc.room,
                sc.tutor,
            ]

        serializer = CelcatExportSerializer(to_serialize_list, many=True)
        return Response(serializer.data)
