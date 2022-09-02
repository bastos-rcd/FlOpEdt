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


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.User
        fields = '__all__'


class UserDepartmentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.UserDepartmentSettings
        fields = '__all__'


class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Tutor
        fields = ['username', 'first_name', 'last_name', 'email']


class TutorUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Tutor
        fields = ['username']


class SupplyStaffsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.SupplyStaff
        fields = '__all__'


class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Student
        fields = '__all__'


class StudentPreferencesSerializer(serializers.Serializer):
    student = serializers.CharField()
    morning_weight = serializers.IntegerField()
    free_half_day_weight = serializers.IntegerField()

    class Meta:
        model = pm.Preferences
        fields = ['student', 'morning_weight', 'free_half_day_weight']


class GroupPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.Preferences
        fields = ['group', 'morning_weight', 'free_half_day_weight']

class StudentInfoSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    department = serializers.SerializerMethodField()
    train_prog = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    def get_department(self, obj):
        if obj.generic_groups.exists():
            return obj.generic_groups.first().train_prog.department.abbrev
        else:
            return

    def get_train_prog(self, obj):
        if obj.generic_groups.exists():
            return obj.generic_groups.first().train_prog.abbrev
        else:
            return

    def get_groups(self, obj):
        if obj.generic_groups.exists():
            return [{'id':g.id, 'name':g.name} for g in obj.generic_groups.all()]
        else:
            return
