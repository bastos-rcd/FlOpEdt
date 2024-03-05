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

from typing import List
from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
import base.models as bm


class StructuralGroupsSerializer(serializers.ModelSerializer):
    type_id = serializers.IntegerField(source="type.id")
    train_prog_id = serializers.IntegerField(source="train_prog.id")
    parent_ids = serializers.SerializerMethodField()

    class Meta:
        model = bm.StructuralGroup
        fields = ("id", "name", "train_prog_id", "type_id", "parent_ids")

    @extend_schema_field(List[OpenApiTypes.INT])
    def get_parent_ids(self, obj):
        return [parent.id for parent in obj.parent_groups.all()]


class TransversalGroupsSerializer(serializers.ModelSerializer):
    type_id = serializers.IntegerField(source="type.id")
    train_prog_id = serializers.IntegerField(source="train_prog.id")
    conflicting_group_ids = serializers.SerializerMethodField()
    parallel_group_ids = serializers.SerializerMethodField()

    class Meta:
        model = bm.TransversalGroup
        fields = (
            "id",
            "name",
            "train_prog_id",
            "type_id",
            "conflicting_group_ids",
            "parallel_group_ids",
        )

    @extend_schema_field(List[OpenApiTypes.INT])
    def get_conflicting_group_ids(self, obj):
        return [
            conflicting_group.id for conflicting_group in obj.conflicting_groups.all()
        ]

    @extend_schema_field(List[OpenApiTypes.INT])
    def get_parallel_group_ids(self, obj):
        return [parallel_group.id for parallel_group in obj.parallel_groups.all()]


class TrainingProgrammesSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField(source="department.id")

    class Meta:
        model = bm.TrainingProgramme
        fields = ("id", "name", "abbrev", "department_id")


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Department
        fields = "__all__"
