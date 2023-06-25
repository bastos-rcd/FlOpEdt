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
import people.models as pm
import base.models as bm


class TutorSerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField()

    def get_departments(self, obj):
        if obj.is_superuser:
            for dep in bm.Department.objects.all():
                yield {'departmentId': dep.id, 'is_admin': 'true'} 
        else:
            for dep in obj.departments.all():
                if obj.has_department_perm:
                    yield {'departmentId': dep.id, 'is_admin': 'true'} 
                else:
                    yield {'departmentId': dep.id, 'is_admin': 'false'}

    class Meta:
        model = pm.Tutor
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'rights', 'departments')


class StudentSerializer(serializers.ModelSerializer):
    department_ids = serializers.IntegerField(source='departments.id', many=True)

    class Meta:
        model = pm.Student
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'rights', 'department_ids')