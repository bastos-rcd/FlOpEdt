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
from rest_framework import viewsets

from api.permissions import IsAdminOrReadOnly
from api.v1.permissions import DjangoModelPermissionsOrReadOnly

import base.models as bm

from . import serializers

### Groups ###


class TrainingProgramsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name="department__abbrev")

    class Meta:
        model = bm.TrainingProgramme
        fields = ["dept"]


class StructuralGroupsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name="train_prog__department__abbrev")

    class Meta:
        model = bm.StructuralGroup
        fields = ["dept"]


class TransversalGroupsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name="train_prog__department__abbrev")

    class Meta:
        model = bm.TransversalGroup
        fields = ["dept"]


class GenericGroupsViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        dept_abbrev = self.request.query_params.get("dept", None)
        if dept_abbrev is None:
            return self.queryset
        return self.queryset.filter(train_prog__department__abbrev=dept_abbrev)


class StructuralGroupsViewSet(GenericGroupsViewSet):
    """
    Structural groups
    """

    queryset = bm.StructuralGroup.objects.all()
    serializer_class = serializers.StructuralGroupsSerializer
    filterset_class = StructuralGroupsFilterSet
    permission_classes = [DjangoModelPermissionsOrReadOnly]


class TransversalGroupsViewSet(GenericGroupsViewSet):
    """
    Transversal groups
    """

    queryset = bm.TransversalGroup.objects.all()
    serializer_class = serializers.TransversalGroupsSerializer
    filterset_class = TransversalGroupsFilterSet
    permission_classes = [DjangoModelPermissionsOrReadOnly]


class TrainingProgramsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programs

    Can be filtered as wanted with parameter="dept"[required]
    of a TrainingProgramme object, with the function TrainingProgramsFilterSet
    """

    def get_queryset(self):
        dept_abbrev = self.request.query_params.get("dept", None)
        if dept_abbrev is None:
            return self.queryset
        return self.queryset.filter(department__abbrev=dept_abbrev)

    queryset = bm.TrainingProgramme.objects.all()
    serializer_class = serializers.TrainingProgrammesSerializer
    filterset_class = TrainingProgramsFilterSet
    permission_classes = [IsAdminOrReadOnly]


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Departments of the organisation
    """

    queryset = bm.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [DjangoModelPermissionsOrReadOnly]