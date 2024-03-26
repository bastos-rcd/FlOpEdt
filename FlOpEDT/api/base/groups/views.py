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
from rest_framework import viewsets
from rest_framework.decorators import action

import base.models as bm
from api.base.groups import serializers
from api.permissions import IsAdminOrReadOnly
from base import queries


class GroupTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group types

    Can be filtered as wanted with every field of a GroupType object.
    """

    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.GroupType.objects.all()
    serializer_class = serializers.GroupTypesSerializer


"""class GenericGroupsFilterSet(filters.FilterSet):  # A supprimer
    dept = filters.CharFilter(field_name='train_prog__department__abbrev', required=True)

    class Meta:
        model = bm.Group
        fields = ['dept']"""


# Creer class StructuralGroupFilterSet
class StructuralGroupsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(
        field_name="train_prog__department__abbrev", required=True
    )

    class Meta:
        model = bm.StructuralGroup
        fields = ["dept"]


# Creer class TransversalGroupFilterSet
class TransversalGroupsFilterSet(filters.FilterSet):
    dept = filters.CharFilter(
        field_name="train_prog__department__abbrev", required=True
    )

    class Meta:
        model = bm.TransversalGroup
        fields = ["dept"]


class StructuralGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the groups

    Can be filtered as wanted with parameter="dept"[required] of a Group object, with the function GroupsFilterSet
    """

    serializer_class = serializers.StructuralGroupSerializer
    queryset = bm.StructuralGroup.objects.all()
    filterset_class = StructuralGroupsFilterSet

    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=["GET"])
    def tree(self, req):
        groups_filtered = StructuralGroupsFilterSet(data=req.query_params)
        if not groups_filtered.is_valid():
            return HttpResponse("KO")
        department = groups_filtered.data.get("dept")

        groups = queries.get_groups(department)
        # groups_serialized = serializers.GroupTreeSerializer(data=groups, many=True)

        return JsonResponse(groups, safe=False)


class TransversalGroupViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TransversalGroupSerializer
    queryset = bm.TransversalGroup.objects.all()
    filterset_class = TransversalGroupsFilterSet
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        abbrev = self.request.query_params.get("dept", None)
        return self.queryset.filter(train_prog__department__abbrev=abbrev)
