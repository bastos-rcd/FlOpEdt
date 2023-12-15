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

from distutils.util import strtobool
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
import base.models as bm
import people.models as pm

import django_filters.rest_framework as filters

from drf_yasg import openapi
from api.preferences import serializers
from api.shared.params import (
    week_param,
    year_param,
    user_param,
    dept_param,
    from_date_param,
    to_date_param,
    date_param,
    weekday_param,
)
from datetime import datetime


from api.permissions import IsTutorOrReadOnly, IsAdminOrReadOnly, IsTutor


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            date_param(required=True),
            user_param(),
            dept_param(),
            openapi.Parameter(
                "tutors-only",
                openapi.IN_QUERY,
                description="only tutors teaching in this week",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
    ),
)
class DatedUserPreferenceViewSet(viewsets.ModelViewSet):
    """
    Helper for user preferences:
    - read parameters
    - build queryset
    """

    permission_classes = [IsAdminOrReadOnly]

    serializer_class = serializers.UserPreferenceSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = {}
        self.select = []
        self.prefetch = []

    def get_queryset(self):
        # set initial parameters
        self.set_common_params()
        self.set_singular_params()
        teach_only = self.request.query_params.get("teach-only", None)
        teach_only = False if teach_only is None else strtobool(teach_only)

        # get teaching teachers only
        if teach_only:
            course_params = {}
            course_params["day"] = self.params["day"]
            if "user__departments__abbrev" in self.params:
                course_params["module__train_prog__department__abbrev"] = self.params[
                    "user__departments__abbrev"
                ]
            teaching_ids = (
                bm.Course.objects.select_related(*course_params.keys())
                .filter(**course_params)
                .distinct("tutor")
                .exclude(tutor__isnull=True)
                .values_list("tutor__id", flat=True)
            )
            if self.request.user.is_authenticated:
                teaching_ids = list(teaching_ids)
                teaching_ids.append(self.request.user.id)
            self.params["user__id__in"] = teaching_ids

        # get preferences in singular week
        qs = super().get_queryset()

        # get users in play
        if teach_only:
            users = teaching_ids
        else:
            filter_user = {}
            users = pm.User.objects
            if "user__username" in self.params:
                filter_user["username"] = self.params["user__username"]
            if "user__departments__abbrev" in self.params:
                filter_user["departments__abbrev"] = self.params[
                    "user__departments__abbrev"
                ]
                users = users.prefetch_related("departments")
            users = users.filter(**filter_user).values_list("id", flat=True)

        # get users with no singular week
        singular_users = qs.distinct("user__username").values_list(
            "user__id", flat=True
        )
        users = set(users).difference(set(singular_users))

        # get remaining preferences in default week
        if len(users) != 0:
            self.params["user__id__in"] = list(users)
            self.set_default_params()
            qs_def = super().get_queryset()
            qs = qs | qs_def

        return qs
