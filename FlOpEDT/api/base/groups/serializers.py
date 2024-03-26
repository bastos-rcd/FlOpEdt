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


class GroupTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.GroupType
        fields = "__all__"


class StructuralGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.StructuralGroup
        fields = "__all__"


# STAGE J'ai crée en dessous


class StructuralShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.StructuralGroup
        fields = ("name",)


class TransversalGroupSerializer(serializers.ModelSerializer):
    train_prog = serializers.CharField(source="train_prog.abbrev")
    conflicting_groups = StructuralShortSerializer(
        many=True
    )  # serializers.CharField(source="conflicting_groups.name",many=True)
    #    parallel_groups = serializers.CharField(source="parallel_groups.name",many=True)

    class Meta:
        model = bm.TransversalGroup
        fields = "__all__"


# J'ai crée au dessus
