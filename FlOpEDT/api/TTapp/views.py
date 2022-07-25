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
from TTapp.FlopConstraint import FlopConstraint, all_subclasses
from base.models import Department
import TTapp.TTConstraints.visio_constraints as ttv
from django.contrib.postgres.fields.array import ArrayField
from base.timing import all_possible_start_times

from drf_yasg import openapi
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from api.TTapp import serializers
from api.permissions import IsAdminOrReadOnly
from base.weeks import current_year

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
                      manual_parameters=[week_param(),
                                         year_param(),
                                         dept_param()])
                  )
class FlopConstraintListViewSet(viewsets.ViewSet):
    """
    ViewSet to see all the constraints and their parameters

    Result can be filtered by week, year and dept
    """
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = '__all__'

    def list(self, request, **kwargs):
        # Getting all the filters
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)
        dept = self.request.query_params.get('dept', None)
        data = list()
        constraintlist = all_subclasses(FlopConstraint)

        for constraint in constraintlist:

            if constraint._meta.abstract == False:
                queryset = constraint.objects.all().select_related('department')

                if week is not None:
                    queryset = queryset.filter(weeks__nb=week)

                if year is not None:
                    queryset = queryset.filter(weeks__year=year)

                if dept is not None:
                    queryset = queryset.filter(department__abbrev=dept)

                for object in queryset:
                    serializer = serializers.TTConstraintSerializer(object)
                    data.append(serializer.data)

        return Response(data)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[week_param(), year_param(), dept_param()])
                  )
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(
                      manual_parameters=[week_param(),
                                         year_param(),
                                         dept_param()])
                  )
class FlopConstraintViewSet(viewsets.ViewSet):
    """
    ViewSet to see all the constraints and their parameters

    Result can be filtered by week, year and dept
    """
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = '__all__'
    lookup_field = 'id'
    lookup_value_regex = '[0-9]{1,32}'

    def list(self, request, **kwargs):
        name = kwargs['name']
        # Getting all the filters
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)
        dept = self.request.query_params.get('dept', None)
        data = list()

        constraint = apps.get_model('TTapp', name)
        if constraint._meta.abstract == False:
            queryset = constraint.objects.all().select_related('department')

            if week is not None:
                queryset = queryset.filter(weeks__nb=week)

            if year is not None:
                queryset = queryset.filter(weeks__year=year)

            if dept is not None:
                queryset = queryset.filter(department__abbrev=dept)

            for object in queryset:
                serializer = serializers.TTConstraintSerializer(object)
                data.append(serializer.data)
        return Response(data)

    def retrieve(self, request, name, id):
        #name = request.query_params.get('name', None)
        # Obtenir la contrainte à partir du nom
        constraint = apps.get_model('TTapp', name)

        instance = constraint.objects.get(pk=id)
        serializer = serializers.TTConstraintSerializer(instance)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        model = apps.get_model('TTapp', request.data['name'])
        serializer = serializers.flopconstraint_serializer_factory(model)(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, name, id):
        response = "{{'message': '{}'}}"

        try:
            model = apps.get_model('TTapp', name)
        except LookupError:
            return Response(response.format('Given constraint name does not exist'))
        try:
            instance = model.objects.get(id=id)
        except:
            return Response(response.format(f'Could not find constraint {name} with id {id}'))
        serializer = serializers.flopconstraint_serializer_factory(model)(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, name, id):
        response = "{{'message': '{}'}}"

        try:
            model = apps.get_model('TTapp', name)
        except LookupError:
            return Response(response.format('Given constraint name does not exist'))
        try:
            instance = model.objects.get(id=id)
        except:
            return Response(response.format(f'Could not find constraint {name} with id {id}'))
        instance.delete()
        return Response(response.format('Deleted successfully'))


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                  )
                  )
class FlopConstraintTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request):
        classes = []
        excluded_fields = {'id', 'class_name',
                           'department', 'weight', 'title', 'comment',
                           'is_active', 'modified_at', 'courses'}

        for constraint_class in all_subclasses(FlopConstraint):
            fields = constraint_class._meta.get_fields()

            parameters_fields = set([f for f in fields
                                     if f.name not in excluded_fields])
            classes.append({'name': constraint_class.__name__, 'local_name': constraint_class._meta.verbose_name,
                            'parameters': parameters_fields})

        serializer = serializers.FlopConstraintTypeSerializer(classes, many=True)
        return Response(serializer.data)


class NoVisioViewSet(viewsets.ModelViewSet):
    queryset = ttv.NoVisio.objects.all()
    serializer_class = serializers.NoVisioSerializer
    permission_classes = [IsAdminOrReadOnly]


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=True)
                      ])
                  )
class FlopConstraintFieldViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request):
        dept = self.request.query_params.get('dept', None)
        if dept is None:
            raise APIException(detail='Department not provided')
        try:
            department = Department.objects.get(abbrev=dept)
        except Department.DoesNotExist:
            raise APIException(detail='Unknown department')
        flop_constraints_fields = set()
        # exclude useless fields
        excluded_fields = {'id', 'class_name',
                           'department', 'weight', 'title', 'comment',
                           'is_active', 'modified_at', 'courses'}

        for constraint_class in all_subclasses(FlopConstraint):
            fields = constraint_class._meta.get_fields()
            # Exclude already considered fields
            excluded_fields |= set(f.name for f in flop_constraints_fields)
            parameters_fields = set([f for f in fields
                                     if f.name not in excluded_fields])
            flop_constraints_fields |= parameters_fields

        fields_list = list(flop_constraints_fields)

        for field in fields_list:
            acceptable = []
            if not field.many_to_one and not field.many_to_many:
                typename = type(field).__name__

                # Récupère les validators dans acceptable
                if typename == 'CharField':
                    choices = field.choices
                    if "day" in field.name:
                        acceptable = department.timegeneralsettings.days
                    elif choices is not None:
                        acceptable = [c[0] for c in choices]
                if typename == 'BooleanField':
                    acceptable = [True, False]

                if type(field) is ArrayField:
                    typename = type(field.base_field).__name__
                    # Récupère les choices de l'arrayfield dans acceptable
                    choices = field.base_field.choices
                    if field.name == "possible_start_times":
                        acceptable = all_possible_start_times(department)
                    elif "day" in field.name:
                        acceptable = department.timegeneralsettings.days
                    elif choices is not None:
                        acceptable = choices

            else:
                # Récupère le modele en relation avec un ManyToManyField ou un ForeignKey
                mod = field.related_model
                typenamesplit = str(mod)[8:-2].split(".")
                typename = typenamesplit[0] + "." + typenamesplit[2]
                acceptablelist = mod.objects.values("id")

                # Filtre les ID dans acceptable list en fonction du department
                if field.name in ["tutor", "tutors", "room", "rooms", "possible_rooms"]:
                    acceptablelist = acceptablelist.filter(departments=department)

                elif field.name in ["train_progs", "course_type", "course_types"]:
                    acceptablelist = acceptablelist.filter(department=department)

                elif field.name in ["modules", "module", "groups", "group"]:
                    acceptablelist = acceptablelist.filter(train_prog__department=department)

                elif field.name == "weeks":
                    acceptablelist = acceptablelist.filter(year__in=[current_year, current_year + 1])

                for element in acceptablelist:
                    acceptable.append(element["id"])

            field.type = typename
            field.acceptable = acceptable
        serializer = serializers.FlopConstraintFieldSerializer(fields_list, many=True)
        return Response(serializer.data)
