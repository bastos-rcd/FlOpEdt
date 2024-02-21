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
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.permissions import DjangoObjectPermissions, DjangoModelPermissions

from rules.contrib.rest_framework import AutoPermissionViewSetMixin

import people.models as pm
import base.models as bm
from api.v1.people.serializers import (
    UserSerializer,
    StudentSerializer,
    ThemePreferencesSerializer,
)

from api.permissions import IsAdminOrReadOnly


class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users

    Can be filtered as wanted with every field of a User object.
    """

    permission_classes = [IsAdminOrReadOnly]
    queryset = pm.User.objects.all()
    serializer_class = UserSerializer


class getCurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class TutorsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users

    Can be filtered as wanted with every field of a User object.
    """

    permission_classes = [IsAdminOrReadOnly]
    queryset = pm.Tutor.objects.all()
    serializer_class = UserSerializer


class StudentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the users

    Can be filtered as wanted with eveUserSerializerry field of a User object.
    """

    permission_classes = [IsAdminOrReadOnly]
    queryset = pm.Student.objects.all()
    serializer_class = StudentSerializer


class ThemePreferenceViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = pm.ThemesPreferences.objects.all()
    serializer_class = ThemePreferencesSerializer
    # permission_classes = [DjangoObjectPermissions]


# from rules.contrib.rest_framework import AutoPermissionViewSetMixin
