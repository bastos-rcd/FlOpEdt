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

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import exceptions, mixins, viewsets

import base.models as bm

from api.shared.params import (
    dept_id_param,
    from_date_param,
    room_id_param,
    to_date_param,
    user_id_param,
)
from api.v1.availability import serializers
from base.rules import can_view_user_availability


class DatedAvailabilityListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    AvailabilityModel = None

    class Meta:
        abstract = True

    def get_queryset(self):
        # avoid warning
        if getattr(self, "swagger_fake_view", False):
            return bm.RoomAvailability.objects.none()

        # We may find another way to define attributes
        # pylint: disable=attribute-defined-outside-init
        if not hasattr(self, "from_date"):
            self.from_date = dt.datetime.fromisoformat(
                self.request.query_params.get("from_date")
            ).date()
        if not hasattr(self, "to_date"):
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
        if getattr(self, "swagger_fake_view", False):
            return bm.RoomAvailability.objects.none()

        ret = super().get_queryset()

        room_id = self.request.query_params.get("room_id", None)
        dept_id = self.request.query_params.get("dept_id", None)

        if room_id is None and dept_id is None:
            raise exceptions.NotAcceptable("A room or a department must be entered.")

        if room_id is not None:
            ret = ret.filter(room=int(room_id))
        if dept_id is not None:
            ret = ret.filter(room__departments=int(dept_id))
        return ret


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
        if getattr(self, "swagger_fake_view", False):
            return bm.UserAvailability.objects.none()

        ret = super().get_queryset()

        user_id = self.request.query_params.get("user_id", None)
        dept_id = self.request.query_params.get("dept_id", None)

        if user_id is None and dept_id is None:
            raise exceptions.NotAcceptable("A user or a department must be entered.")
        if user_id is not None:
            user_id = int(user_id)

        if not can_view_user_availability(self.request.user, user_id):
            raise exceptions.PermissionDenied(
                detail="You have no access to these availabilities"
            )

        if user_id is not None:
            ret = ret.filter(user__id=int(user_id))
        if dept_id is not None:
            ret = ret.filter(user__departments=int(dept_id))
        return ret


class UserDatedAvailabilityUpdateViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Availability. Either a room or a department must be entered.
    """

    AvailabilityModel = bm.UserAvailability
    serializer_class = serializers.UserAvailabilityFullDaySerializer
    queryset = bm.UserAvailability.objects.all()


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
        user_id_param(),
        dept_id_param(),
        OpenApiParameter("to_date", exclude=True),
        OpenApiParameter("from_date", exclude=True),
    ],
)
class UserDefaultAvailabilityListViewSet(UserDatedAvailabilityListViewSet):
    def get_queryset(self):
        # pylint: disable=attribute-defined-outside-init
        self.from_date = dt.datetime(1, 1, 1)
        self.to_date = dt.datetime(1, 1, 8)
        return super().get_queryset()


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
        # pylint: disable=attribute-defined-outside-init
        self.from_date = dt.datetime(1, 1, 1)
        self.to_date = dt.datetime(1, 1, 8)
        return super().list(request, *args, **kwargs)


class UserDefaultAvailabilityUpdateViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Update default availability. (Will be pushed in the default week based
    on the weekday of the dates from the query parameters)
    """

    AvailabilityModel = bm.UserAvailability
    serializer_class = serializers.UserAvailabilityDefaultWeekSerializer
    queryset = bm.UserAvailability.objects.all()


class RoomDefaultAvailabilityUpdateViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Update default availability. (Will be pushed in the default week
    based on the weekday of the dates from the query parameters)
    """

    AvailabilityModel = bm.UserAvailability
    serializer_class = serializers.RoomAvailabilityDefaultWeekSerializer
    queryset = bm.RoomAvailability.objects.all()