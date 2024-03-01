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

from distutils.util import strtobool

from rules.contrib.rest_framework import AutoPermissionViewSetMixin
from rules.contrib.views import PermissionRequiredMixin

from rest_framework import viewsets, exceptions, mixins, parsers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_spectacular.utils import extend_schema

import django_filters.rest_framework as filters
from django.utils.decorators import method_decorator

from base.timing import date_to_flopday, Day

import base.models as bm
import people.models as pm

from api.v1.availability import serializers
from api.permissions import IsTutorOrReadOnly, IsAdminOrReadOnly, IsTutor
from api.shared.params import (
    user_id_param,
    room_id_param,
    dept_param,
    dept_id_param,
    from_date_param,
    to_date_param,
)


class DatedAvailabilityListViewSet(
    AutoPermissionViewSetMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Availability. Either a user or a department must be entered.
    """

    # permission_classes = [IsAdminOrReadOnly]

    class Meta:
        abstract = True

    def get_queryset(self):
        # avoid warning
        if getattr(self, "swagger_fake_view", False):
            return bm.RoomAvailability.objects.none()

        self.from_date = dt.datetime.fromisoformat(
            self.request.query_params.get("from_date")
        ).date()
        self.to_date = dt.datetime.fromisoformat(
            self.request.query_params.get("to_date")
        ).date()

        if self.from_date > self.to_date:
            raise exceptions.NotAcceptable(
                '"from_date" parameter is later than "to_date" parameter'
            )

        return self.AvailabilityModel.objects.filter(
            date__gte=self.from_date, date__lt=self.to_date
        )


@extend_schema(
    parameters=[
        from_date_param(required=True),
        to_date_param(required=True),
        room_id_param(),
        dept_id_param(),
    ],
)
class RoomDatedAvailabilityListViewSet(DatedAvailabilityListViewSet):
    """
    Availability. Either a room or a department must be entered.
    """

    AvailabilityModel = bm.RoomAvailability
    serializer_class = serializers.RoomAvailabilitySerializer

    def get_queryset(self):

        ret = super(RoomDatedAvailabilityListViewSet, self).get_queryset()

        room_id = self.request.query_params.get("room_id", None)
        dept_id = self.request.query_params.get("dept_id", None)

        if room_id is None and dept_id is None:
            raise exceptions.NotAcceptable("A room or a department must be entered.")

        if room_id is not None:
            ret = ret.filter(room=int(room_id))
        if dept_id is not None:
            ret = ret.filter(room__departments=int(dept_id))
        return ret


class RoomDatedAvailabilityUpdateViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Update availability. Should cover the whole period between from_date and to_date
    """

    AvailabilityModel = bm.RoomAvailability
    serializer_class = serializers.RoomAvailabilityFullDaySerializer


@extend_schema(
    parameters=[
        from_date_param(required=True),
        to_date_param(required=True),
        user_id_param(),
        dept_id_param(),
    ],
)
class UserDatedAvailabilityListViewSet(DatedAvailabilityListViewSet):
    """
    Availability. Either a user or a department must be entered.
    """

    AvailabilityModel = bm.UserAvailability
    serializer_class = serializers.UserAvailabilitySerializer

    def get_queryset(self):
        ret = super(UserDatedAvailabilityListViewSet, self).get_queryset()

        user_id = self.request.query_params.get("user_id", None)
        dept_id = self.request.query_params.get("dept_id", None)

        if user_id is None and dept_id is None:
            raise exceptions.NotAcceptable("A user or a department must be entered.")

        if user_id is not None:
            ret = ret.filter(user__id=int(user_id))
        if dept_id is not None:
            ret = ret.filter(user__departments=dept_id)
        return ret


class UserDatedAvailabilityUpdateViewSet(
    AutoPermissionViewSetMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Availability. Either a room or a department must be entered.
    """

    AvailabilityModel = bm.UserAvailability
    serializer_class = serializers.UserAvailabilityFullDaySerializer
    queryset = bm.UserAvailability.objects.all()


@extend_schema(
    parameters=[
        user_id_param(),
        dept_id_param(),
    ],
)
class UserDefaultAvailabilityListViewSet(UserDatedAvailabilityListViewSet):
    def list(self, request, *args, **kwargs):
        self.from_date = dt.datetime(1, 1, 1)
        self.to_date = dt.datetime(1, 1, 8)
        return super(UserDefaultAvailabilityListViewSet, self).list(
            request, *args, **kwargs
        )


@extend_schema(
    parameters=[
        room_id_param(),
        dept_id_param(),
    ],
)
class RoomDefaultAvailabilityListViewSet(RoomDatedAvailabilityListViewSet):
    """
    Default availability. Either a room or a department must be entered.
    """

    def list(self, request, *args, **kwargs):
        self.from_date = dt.datetime(1, 1, 1)
        self.to_date = dt.datetime(1, 1, 8)
        return super(RoomDefaultAvailabilityListViewSet, self).list(
            request, *args, **kwargs
        )
