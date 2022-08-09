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
from django.utils.decorators import method_decorator
import django_filters.rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


import people.models as pm
import base.models as bm
from api.people import serializers
from api.shared.params import week_param, year_param

from api.permissions import IsTutorOrReadOnly, IsAdminOrReadOnly


class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users

    Can be filtered as wanted with every field of a User object.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = pm.User.objects.all()
    serializer_class = serializers.UsersSerializer


class UserDepartmentSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the user department settings
    which shows the combination of the user and the department

    Can be filtered as wanted with every field of a User Department object.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = pm.UserDepartmentSettings.objects.all()
    serializer_class = serializers.UserDepartmentSettingsSerializer


class SupplyStaffsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the supply staff

    Can be filtered as wanted with every field of a Supply Staff object.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = pm.SupplyStaff.objects.all()
    serializer_class = serializers.SupplyStaffsSerializer


class StudentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the students

    Can be filtered as wanted with every field of a Student object.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = pm.Student.objects.all()
    serializer_class = serializers.StudentsSerializer


class StudentInfoViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all info of one student
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = pm.Student.objects.all()
    serializer_class = serializers.StudentInfoSerializer


# class StudentPreferencesViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet to see all the students' preferences.

#     Can be filtered as wanted with every field of a StudentPreference object.
#     """
#     permission_classes = (IsAuthenticated,)
#     serializer_class = serializers.StudentPreferencesSerializer
#     filterset_fields = '__all__'

#     def get_queryset(self):
#         # Creating a queryset containing every StudentPreference
#         qs = pm.StudentPreferences.objects.all()

#         # Getting the filters
#         username = self.request.query_params.get('username', None)

#         # Applying filters
#         if username == None:
#             return None
#         return qs.filter(username=username)


# class GroupPreferencesViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet to see all the groups' preferences.

#     Can be filtered as wanted with every field of a GroupPreference object.
#     """
#     permission_classes = (IsAuthenticated,)
#     queryset = pm.GroupPreferences.objects.all()
#     serializer_class = serializers.GroupPreferencesSerializer


class TutorFilterSet(filters.FilterSet):
    permission_classes = [IsTutorOrReadOnly]
    dept = filters.CharFilter(field_name='departments__abbrev', required=True)

    class Meta:
        model = pm.Tutor
        fields = ['dept']


class TutorUsernameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the tutors

    Can be filtered as wanted with every field of a Tutor object.
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = pm.Tutor.objects.all()
    serializer_class = serializers.TutorUsernameSerializer
    filter_class = TutorFilterSet


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      operation_description="Active tutors",
                      manual_parameters=[week_param(), year_param()])
                  )
class TutorViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Getting all the filters
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)

        # Filtering
        if week is not None and year is not None:
            return pm.Tutor.objects.filter(
                pk__in=bm.ScheduledCourse.objects.filter(
                    course__week__nb=week,
                    course__week__year=year) \
                    .distinct('tutor').values('tutor')
            )
        else:
            return pm.Tutor.objects.all()

    serializer_class = serializers.TutorSerializer
    filter_class = TutorFilterSet
    permission_classes = [IsAdminOrReadOnly]
