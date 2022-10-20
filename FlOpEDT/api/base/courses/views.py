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

from drf_yasg.utils import swagger_auto_schema

from api.base.courses import serializers
from rest_framework import viewsets
import django_filters.rest_framework as filters
import base.models as bm

from django.utils.decorators import method_decorator
from api.shared.params import week_param, year_param, dept_param
from api.shared.views_set import ListGenericViewSet

from api.permissions import IsTutorOrReadOnly, IsAdminOrReadOnly

@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_description='If (week,year) is given, any module that is taught in this week',
        manual_parameters=[week_param(),
                           year_param(),
                           dept_param(required=True)])
)
class ModuleViewSet(viewsets.ModelViewSet):
    """
    Modules in a given department

    TODO: (Header for list)

    """
    permission_classes = [IsAdminOrReadOnly]
    
    queryset = bm.Module.objects.all()
    serializer_class = serializers.ModuleSerializer
    filterset_fields = '__all__'

    def get_queryset(self):
        # Get the filters from the request
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)
        abbrev=self.request.query_params.get('dept', None)

        # Applying filters
        if week is not None and year is not None:
            # Those 2 filters are needed to have returned data
            # distinct method allows us to get each module only once
            qs = bm.ScheduledCourse.objects.distinct('course__module').filter(course__week__nb=week, course__week__year=year)
            # Filtering with department
            qs = qs.filter(course__module__train_prog__department__abbrev=abbrev)

            # Getting every module that appears
            qs_module = qs.values('course__module')
            # Get all the modules that appears in the scheduled courses. Those primary keys come from the previous line
            return bm.Module.objects.filter(pk__in=qs_module)
        else:
            return bm.Module.objects.filter(train_prog__department__abbrev=abbrev)


class ModuleFullViewSet(ListGenericViewSet):
    """
    ViewSet to see all the modules that have a Scheduled course in a given week/year couple.

    can also be filtered with a department.
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.Module.objects.all()
    serializer_class = serializers.ModuleFullSerializer
    filterset_fields = '__all__'


class CourseTypeFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='department__abbrev', required=True)

    class Meta:
        model = bm.CourseType
        fields = ['dept']


class CourseTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course types.

    Can be filtered as wanted with the department of a CourseType object, with the function CourseTypesFilterSet
    """
    queryset = bm.CourseType.objects.all()
    serializer_class = serializers.CourseTypeSerializer
    filter_class = CourseTypeFilterSet

    filterset_fields = '__all__'

    permission_classes = [IsAdminOrReadOnly]


class CourseTypeNameViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the course types.

    Can be filtered as wanted with the department of a CourseType object, with the function CourseTypesFilterSet
    """
    queryset = bm.CourseType.objects.all()
    serializer_class = serializers.CourseTypeNameSerializer
    filter_class = CourseTypeFilterSet

    filterset_fields = '__all__'

    permission_classes = [IsAdminOrReadOnly]


class CourseFilterSet(filters.FilterSet):
    dept = filters.CharFilter(field_name='module__train_prog__department__abbrev', required=False)
    week = filters.NumberFilter(field_name='week__nb', required=False)
    year = filters.NumberFilter(field_name='week__year', required=False)

    class Meta:
        model = bm.Course
        fields = ['dept', 'week', 'year']


class CoursesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the courses

    Can be filtered as wanted with every field of a Course object.
    """
    queryset = bm.Course.objects.all() \
    .prefetch_related('week', 'type', 'room_type', 'groups', 'module', 'modulesupp')
    serializer_class = serializers.CoursesSerializer
    filter_class = CourseFilterSet

    filterset_fields = '__all__'

    permission_classes = [IsAdminOrReadOnly]
