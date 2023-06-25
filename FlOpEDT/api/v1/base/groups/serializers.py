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

import base.models as bm
from rest_framework import serializers


class StructuralGroupsSerializer(serializers.ModelSerializer):
    train_prog_id = serializers.IntegerField(source='train_prog.id')
    parents_ids = serializers.IntegerField(source='parent_groups.id', many=True)
    
    class Meta:
        model = bm.StructuralGroup
        fields = ('id', 'name', 'train_prog_id', 'type', 'parents_ids')


class TransversalGroupsSerializer(serializers.ModelSerializer): 
    train_prog_id = serializers.IntegerField(source='train_prog.id')
    conflicting_groups_ids = serializers.IntegerField(source='conflicting_groups.id', many=True)
    parallel_groups_ids = serializers.IntegerField(source='parallel_groups.id', many=True)
        
    
    class Meta:
        model = bm.TransversalGroup
        fields = ('id', 'name', 'train_prog_id', 'type', 'conflicting_groups_ids', 'parallel_groups_ids')


class TrainingProgrammesSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField(source='department.id')

    class Meta:
        model = bm.TrainingProgramme
        fields = ('id', 'name', 'abbrev', 'department_id')