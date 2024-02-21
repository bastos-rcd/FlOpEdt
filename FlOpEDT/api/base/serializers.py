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
import people.models as pm
from rest_framework import serializers


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Department
        fields = '__all__'


# ------------
# -- TIMING --
# ------------

class HolidaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Holiday
        fields = '__all__'


class TrainingHalfDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TrainingHalfDay
        fields = '__all__'


class TrainingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TrainingPeriod
        fields = "__all__"


class TimeGeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TimeGeneralSettings
        fields = '__all__'


class WeeksSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Week
        fields = '__all__'

# -----------------
# - MODIFICATIONS -
# -----------------

class EdtVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.EdtVersion
        fields = '__all__'


class CourseModificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.CourseModification
        fields = '__all__'


# -----------
# -- COSTS --
# -----------

class TutorCostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TutorCost
        fields = '__all__'


class GroupCostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.GroupCost
        fields = '__all__'


class GroupFreeHalfDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.GroupFreeHalfDay
        fields = '__all__'


#                                  --------------------                                 #
#                                  ----Course Types----                                 #
#                                  --------------------                                 #

# ----------
# -- MISC --
# ----------

class DependenciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Dependency
        fields = '__all__'


class CourseStartTimeConstraintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.CourseStartTimeConstraint
        fields = '__all__'


class RegensSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.Regen
        fields = '__all__'

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.User
        fields = '__all__'


class LogoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = pm.User
        fields = '__all__'


#                                -------------------------                              #
#                                ----Training Programs----                              #
#                                -------------------------                              #


class TrainingProgrammeNameSerializer(serializers.ModelSerializer):
    abbrev = serializers.CharField()

    class Meta:
        model = bm.TrainingProgramme
        fields = ['abbrev']


class TrainingProgrammeSerializer(serializers.ModelSerializer):
    abbrev = serializers.CharField()

    class Meta:
        model = bm.TrainingProgramme
        fields = ['abbrev', 'name']


class TrainingProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TrainingProgramme
        fields = '__all__'
