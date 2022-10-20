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

from rest_framework import serializers

import base.models as bm
from api.fetch.serializers import IDRoomSerializer


class RoomTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    basic_rooms = IDRoomSerializer(many=True)

    class Meta:
        model = bm.Room
        fields = ['id', 'name', 'subroom_of', 'departments', 'is_basic', 'basic_rooms']


class RoomNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Room
        fields = ['name']


class RoomSortsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.RoomSort
        fields = '__all__'


class RoomAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        model = bm.RoomAttribute
        fields = '__all__'


class BooleanRoomAttributeSerializer(RoomAttributeSerializer):
    class Meta:
        model = bm.BooleanRoomAttribute
        fields = '__all__'


class NumericRoomAttributeSerializer(RoomAttributeSerializer):
    class Meta:
        model = bm.NumericRoomAttribute
        fields = '__all__'


class BooleanRoomAttributeValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.BooleanRoomAttributeValue
        fields = '__all__'


class NumericRoomAttributeValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.NumericRoomAttributeValue
        fields = '__all__'
