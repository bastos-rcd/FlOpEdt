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

from api.shared.params import dept_param, week_param, year_param
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from django.apps import apps
import TTapp.TTConstraints.TTConstraint as ttc
import TTapp.TTConstraints.visio_constraints as ttv

from drf_yasg import openapi
from rest_framework import viewsets
from rest_framework.response import Response
from api.TTapp import serializers
from api.permissions import IsAdminOrReadOnly

# ---------------
# ---- TTAPP ----
# ---------------
""" 

class TTCustomConstraintsViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the TTCustomConstraints.

    Can be filtered as wanted with every field of a CustomContraint object.
    
    queryset = ttm.CustomConstraint.objects.all()
    serializer_class = serializers.TTCustomConstraintsSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTLimitCourseTypeTimePerPeriodsViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the LimitCourseTypeTimePerPeriods.

    Can be filtered as wanted with every field of a LimitCourseTypeTimePerPeriods object.
    
    queryset = ttm.LimitCourseTypeTimePerPeriod.objects.all()
    serializer_class = serializers.TTLimitCourseTypeTimePerPeriodsSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTReasonableDaysViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the ReasonableDays.

    Can be filtered as wanted with every field of a ReasonableDay object.
    
    queryset = ttm.ReasonableDays.objects.all()
    serializer_class = serializers.TTReasonableDayssSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTStabilizeFilter(filters.FilterSet):
    
    Custom filter for ArrayField fixed_days
    
    fixed_days = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ttm.Stabilize
        fields = ('group', 'module', 'tutor', 'fixed_days')


class TTStabilizeViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the Stabilize objects from TTapp.

    Can be filtered as wanted with "fixed_days"
    of a Stabilize object by calling the function TTStabilizeFilter
    
    queryset = ttm.Stabilize.objects.all()
    serializer_class = serializers.TTStabilizeSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_class = TTStabilizeFilter


class TTMinHalfDaysViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the MinHalfDays.

    Can be filtered as wanted with every field of a MinHalfDay object.
    
    queryset = ttm.MinHalfDays.objects.all()
    serializer_class = serializers.TTMinHalfDaysSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTMinNonPreferedSlotsViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the MinNonPreferedSlots.

    Can be filtered as wanted with every field of a MinNonPreferedSlots object.
    
    queryset = ttm.MinNonPreferedSlot.objects.all()
    serializer_class = serializers.TTMinNonPreferedSlotsSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTAvoidBothTimesViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the AvoidBothTimes.

    Can be filtered as wanted with every field of a AvoidBothTime object.
    
    queryset = ttm.AvoidBothTimes.objects.all()
    serializer_class = serializers.TTAvoidBothTimesSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTSimultaneousCoursesViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the SimultaneousCourses.

    Can be filtered as wanted with every field of a SimultaneousCourse object.
    
    queryset = ttm.SimultaneousCourses.objects.all()
    serializer_class = serializers.TTSimultaneousCoursesSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTLimitedFilter(filters.FilterSet):
    
    Custom filter for ArrayField possible_start_times
    
    possible_start_times = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ttm.LimitedStartTimeChoices
        fields = ('module', 'tutor', 'group', 'type', 'possible_start_times')


class TTLimitedStartTimeChoicesViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the LimitedStartTimeChoices.

    Can be filtered as wanted with "possible_start_times"
    of a LimitedStartChoices object by calling the function TTLimitedFilter
    
    queryset = ttm.LimitedStartTimeChoices.objects.all()
    serializer_class = serializers.TTLimitedStartTimeChoicesSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_class = TTLimitedFilter


class TTLimitedRoomChoicesViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the LimitedRoomChoices.

    Can be filtered as wanted with every field of a LimitedRoomChoice object.
    
    queryset = ttm.LimitedRoomChoices.objects.all()
    serializer_class = serializers.TTLimitedRoomChoicesSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'
 """

@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[week_param(), year_param(), dept_param()])
                  )
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                            openapi.Parameter('name',
                                            openapi.IN_QUERY,
                                            description="Name of constraint",
                                            type=openapi.TYPE_STRING, required = True),
                      ])
                  )
class TTConstraintViewSet(viewsets.ViewSet):
    """
    ViewSet to see all the constraints and their parameters
    
    Result can be filtered by week, year and dept
    """
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = '__all__' 
    serializer_class = serializers.ConstraintSerializer


    def list(self, request):
        # Getting all the filters
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)
        dept = self.request.query_params.get('dept', None)
        data = list()
        constraintlist = ttc.TTConstraint.__subclasses__()

        for constraint in constraintlist :

            if (constraint._meta.abstract == False):
                queryset = constraint.objects.all().select_related('department')

                if week is not None:
                    queryset = queryset.filter(weeks__nb = week)

                if year is not None:
                    queryset = queryset.filter(weeks__year=year)
                
                if dept is not None:
                    queryset = queryset.filter(department__abbrev=dept)

                for object in queryset:
                    serializer = serializers.ConstraintSerializer(object)
                    data.append(serializer.data)

        return Response(data)

    def retrieve(self, request, pk):
        name = request.query_params.get('name', None)
        #Obtenir la contrainte à partir du nom
        constraint = apps.get_model('TTapp', name)

        instance = constraint.objects.get(pk=pk)
        serializer = serializers.ConstraintSerializer(instance)

        return Response(serializer.data)

class NoVisioViewSet(viewsets.ModelViewSet):
    queryset = ttv.NoVisio.objects.all()
    serializer_class = serializers.NoVisioSerializer
    permission_classes = [IsAdminOrReadOnly]