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
from api.shared.params import week_param, year_param, user_param, dept_param


from api.permissions import IsTutorOrReadOnly, IsAdminOrReadOnly, IsTutor

# -----------------
# -- PREFERENCES --
# -----------------


class CourseAvailabilityViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course preferences.

    Can be filtered as wanted with every field of a CourseAvailability object.
    """

    permission_classes = [IsAdminOrReadOnly]
    # permission_classes = (IsTutor,)
    queryset = bm.CourseAvailability.objects.all()
    serializer_class = serializers.CourseAvailabilitySerializer

    filterset_fields = "__all__"


# enabling only GET methods:
# from rest_framework import viewsets, mixins
# class Blabla(mixins.RetrieveModelMixin, viewsets.GenericViewSet)
# (cf https://stackoverflow.com/questions/23639113/disable-a-method-in-a-viewset-django-rest-framework)
#
# TODO check how to generate custom schema with this


class UserAvailabilityViewSet(viewsets.ModelViewSet):
    """
    Helper for user availabilities:
    - read parameters
    - build queryset
    """

    permission_classes = [IsAdminOrReadOnly]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = {}
        self.select = []
        self.prefetch = []

    serializer_class = serializers.UserAvailabilitySerializer

    def set_common_params(self):
        # Getting the filters
        user = self.request.query_params.get("user", None)
        if user is not None:
            self.params["user__username"] = user
            self.select.append("user")
        dept = self.request.query_params.get("dept", None)
        if dept is not None:
            self.params["user__departments__abbrev"] = dept
            self.prefetch.append("user__departments")

    def set_default_params(self):
        self.unset_singular_params()
        self.params["week"] = None

    def set_singular_params(self):
        self.params["week__nb"] = self.request.query_params.get("week")
        self.params["week__year"] = self.request.query_params.get("year")
        self.select.append("week")

    def unset_singular_params(self):
        self.params.pop("week__nb", None)
        self.params.pop("week__year", None)
        try:
            self.select.remove("week")
        except ValueError:
            pass

    def get_queryset(self):
        self.set_common_params()
        return (
            bm.UserAvailability.objects.select_related(*self.select)
            .prefetch_related(*self.prefetch)
            .filter(**self.params)
            .order_by("user__username")
        )


# Custom schema generation: see
# https://drf-yasg.readthedocs.io/en/stable/custom_spec.html
@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[user_param(), dept_param()],
        operation_description="Default user availabilities",
    ),
)
class UserAvailabilityDefaultViewSet(UserAvailabilityViewSet):
    permission_classes = [IsAdminOrReadOnly]

    # permission_classes = [IsTutor]
    def get_queryset(self):
        self.set_default_params()
        return super().get_queryset()


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            week_param(required=True),
            year_param(required=True),
            user_param(),
            dept_param(),
        ],
        operation_description="User availabilities in (week,year)",
    ),
)
class UserAvailabilitySingularViewSet(UserAvailabilityViewSet):
    permission_classes = [IsAdminOrReadOnly]

    # permission_classes = [IsTutor]
    def get_queryset(self):
        self.set_singular_params()
        return super().get_queryset()


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            week_param(required=True),
            year_param(required=True),
            user_param(),
            dept_param(),
            openapi.Parameter(
                "teach-only",
                openapi.IN_QUERY,
                description="only teachers teaching in this week",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
        operation_description="User availabilities in (week,year) if exist otherwise in default week",
    ),
)
class UserAvailabilityActualViewSet(UserAvailabilityViewSet):
    """
    User availabilities in (week, year) if exist. Otherwise, default week.

    Also can be filtered with dept and user
    """

    permission_classes = [IsAdminOrReadOnly]

    # permission_classes = [IsTutor]
    def get_queryset(self):
        # set initial parameters
        self.set_common_params()
        self.set_singular_params()
        teach_only = self.request.query_params.get("teach-only", None)
        teach_only = False if teach_only is None else strtobool(teach_only)

        # get teaching teachers only
        if teach_only:
            course_params = {}
            course_params["week__nb"] = self.params["week__nb"]
            course_params["week__year"] = self.params["week__year"]
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


class RoomAvailabilityDefaultFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name="room__departments__abbrev")
    room = filters.CharFilter(field_name="room__name")

    class Meta:
        model = bm.RoomAvailability
        fields = ["dept", "room"]


class RoomAvailabilityDefaultViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room availabilities

    Can be filtered as wanted with every field of a Room object.
    """

    permission_classes = [IsAdminOrReadOnly]
    # permission_classes = [IsTutor]
    filterset_class = RoomAvailabilityDefaultFilterSet
    queryset = bm.RoomAvailability.objects.filter(week=None)
    serializer_class = serializers.RoomAvailabilitySerializer


class RoomAvailabilitySingularFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name="room__departments__abbrev", required=True)

    class Meta:
        model = bm.RoomAvailability
        fields = ["dept"]


class RoomAvailabilitySingularViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    # permission_classes = [IsTutor]
    filterset_class = RoomAvailabilitySingularFilterSet
    queryset = bm.RoomAvailability.objects.filter()
    serializer_class = serializers.RoomAvailabilitySerializer
