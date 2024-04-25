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
                "de_semaine",
                openapi.IN_QUERY,
                description="semaine initiale",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "de_annee",
                openapi.IN_QUERY,
                description="année initiale",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "a_semaine",
                openapi.IN_QUERY,
                description="semaine finale",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "a_annee",
                openapi.IN_QUERY,
                description="année finale",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "promo",
                openapi.IN_QUERY,
                description="abbréviation de la promo",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ]
    ),
)
class CelcatExportViewSet(viewsets.ViewSet):
    """
    Gestion de la création de fichiers d'export pour Celcat
    """

    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):

        param_exception = NotAcceptable(
            detail=f"Usage : ?de_semaine=xx&de_annee=xy" f"&a_semaine=yx&a_annee=yy"
        )

        wanted_param = ["de_semaine", "de_annee", "a_semaine", "a_annee"]
        supp_filters = {}

        # check that all parameters are given
        for param in wanted_param:
            if param not in request.GET:
                raise param_exception

        dept = self.request.query_params.get("dept", None)
        if dept is not None:
            try:
                dept = Department.objects.get(abbrev=dept)
            except Department.DoesNotExist:
                raise APIException(detail="Unknown department")

        # clean week-year parameters
        week_inter = [
            {
                "year": request.GET.get("de_annee"),
                "min_week": request.GET.get("de_semaine"),
                "max_week": 60,
            },
            {
                "year": request.GET.get("a_annee"),
                "min_week": 1,
                "max_week": request.GET.get("a_semaine"),
            },
        ]
        if week_inter[0]["year"] == week_inter[1]["year"]:
            week_inter[0]["max_week"] = week_inter[1]["max_week"]
            week_inter[1]["max_week"] = 0

        Q_filter_week = Q(course__week__nb__gte=week_inter[0]["min_week"]) & Q(
            course__week__nb__lte=week_inter[0]["max_week"]
        ) & Q(course__week__year=week_inter[0]["year"]) | Q(
            course__week__nb__gte=week_inter[1]["min_week"]
        ) & Q(
            course__week__nb__lte=week_inter[1]["max_week"]
        ) & Q(
            course__week__year=week_inter[1]["year"]
        )

        # clean training programme
        train_prog = self.request.query_params.get("promo", None)
        if train_prog is not None:
            try:
                train_prog = TrainingProgramme.objects.get(
                    department=dept, abbrev=train_prog
                )
                supp_filters["course__module__train_prog"] = train_prog
            except TrainingProgramme.DoesNotExist:
                raise APIException(detail="Unknown training programme")
        considered_scheduled_courses = ScheduledCourse.objects.select_related(
            "course__week", "course__module__train_prog"
        ).filter(
            Q_filter_week,
            course__module__train_prog__department=dept,
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
