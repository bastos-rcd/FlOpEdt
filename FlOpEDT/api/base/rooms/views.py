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

import django_filters.rest_framework as filters
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets

import base.models as bm
from api.base.rooms import serializers
from api.permissions import IsAdminOrReadOnly
from api.shared.params import dept_param
from base import queries


class RoomTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room types

    Can be filtered as wanted with every field of a RoomTypes object.
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.RoomType.objects.all()
    serializer_class = serializers.RoomTypesSerializer
    filterset_fields = '__all__'


class RoomFilterSet(filters.FilterSet):
    permission_classes = [IsAdminOrReadOnly]

    dept = filters.CharFilter(field_name='departments__abbrev', required=False)

    class Meta:
        model = bm.Room
        fields = ['dept']


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the rooms.

    Can be filtered as wanted with parameter="dept"[required] of a Room object, with the function RoomsFilterSet
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomSerializer
    filter_class = RoomFilterSet


class RoomNameViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see a list which shows each room is with what kind of group.

    Can be filtered as wanted with every field of a Room object.
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomNameSerializer
    filter_class = RoomFilterSet


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[dept_param()])
                  )
class RoomAllViewSet(viewsets.ViewSet):
    queryset = bm.Room.objects.all()
    filter_class = RoomFilterSet
    permission_classes = [IsAdminOrReadOnly]

    def list(self, req):
        room_filtered = RoomFilterSet(data=req.query_params)
        if not room_filtered.is_valid():
            return HttpResponse(room_filtered.errors)
        department = room_filtered.data.get('dept')
        rooms = queries.get_room_types_groups(department)
        return JsonResponse(rooms, safe=False)


class RoomSortsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the room sorts.

    Can be filtered as wanted with every field of a RoomSort object.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = bm.RoomSort.objects.all()
    serializer_class = serializers.RoomSortsSerializer

    filterset_fields = '__all__'


class RoomAttributeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the boolean room attributes.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = bm.RoomAttribute.objects.all()
    serializer_class = serializers.RoomAttributeSerializer

    filterset_fields = '__all__'


class BooleanRoomAttributeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the boolean room attributes.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = bm.BooleanRoomAttribute.objects.all()
    serializer_class = serializers.BooleanRoomAttributeSerializer

    filterset_fields = '__all__'


class NumericRoomAttributeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the boolean room attributes.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = bm.NumericRoomAttribute.objects.all()
    serializer_class = serializers.NumericRoomAttributeSerializer

    filterset_fields = '__all__'


class BooleanRoomAttributeValuesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the boolean room attribute values.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = bm.BooleanRoomAttributeValue.objects.all()
    serializer_class = serializers.BooleanRoomAttributeValuesSerializer

    filterset_fields = '__all__'


class NumericRoomAttributeValuesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the boolean room attribute values.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = bm.NumericRoomAttributeValue.objects.all()
    serializer_class = serializers.NumericRoomAttributeValuesSerializer

    filterset_fields = '__all__'
