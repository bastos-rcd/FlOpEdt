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

import django_filters.rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework.response import Response

from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

from django.apps import apps

import base.models as bm
from base import queries, weeks
import people.models as pm
import displayweb.models as dwm
import roomreservation.models as rrm

from api.fetch import serializers
from api.shared.params import dept_param, week_param, year_param, user_param, \
    work_copy_param, group_param, train_prog_param, lineage_param, tutor_param
from api.permissions import IsTutorOrReadOnly, IsAdminOrReadOnly
from base.timing import flopday_to_date, Day, days_list, time_to_floptime

class ScheduledCourseFilterSet(filters.FilterSet):
    # makes the fields required
    week = filters.NumberFilter(field_name='course__week__nb', required=True)
    year = filters.NumberFilter(field_name='course__week__year', required=True)

    class Meta:
        model = bm.ScheduledCourse
        fields = ['week', 'year']


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          # in the filterset
                          week_param(required=True),
                          year_param(required=True),
                          work_copy_param(),
                          # in the get_queryset
                          dept_param(),
                          train_prog_param(),
                          group_param(),
                          lineage_param(),
                          tutor_param()
                      ])
                  )
class ScheduledCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the scheduled courses

    Result can be filtered by function ScheduledCourseFilterSet
    as wanted with week, year and work_copy (0 by default).
    Request needs a department filter.
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_class = ScheduledCourseFilterSet

    def get_queryset(self):
        lineage = self.request.query_params.get('lineage', 'false')
        lineage = True if lineage == 'true' else False
        self.dept = self.request.query_params.get('dept', None)
        if self.dept is not None:
            try:
                self.dept = bm.Department.objects.get(abbrev=self.dept)
            except bm.Department.DoesNotExist:
                raise exceptions.NotAcceptable(detail='Unknown department')

        self.train_prog = self.request.query_params.get('train_prog', None)
        group_name = self.request.query_params.get('group', None)
        self.tutor = self.request.query_params.get('tutor_name', None)
        work_copy = self.request.query_params.get('work_copy', 0)
        if self.tutor is not None:
            try:
                self.tutor = pm.Tutor.objects.get(username=self.tutor)
            except pm.Tutor.DoesNotExist:
                raise exceptions.NotAcceptable(detail='Unknown tutor')

        queryset = bm.ScheduledCourse\
                     .objects.all().select_related('course__module__train_prog__department',
                                                   'tutor__display',
                                                   'course__type',
                                                   'course__room_type',
                                                   'course__module__display')\
            .prefetch_related('course__groups__train_prog',
                              'room',
                              'course__supp_tutor')
        queryset = queryset.filter(work_copy=work_copy)
        # sanity check
        if group_name is not None and self.train_prog is None:
            raise exceptions.NotAcceptable(detail='A training programme should be '
                                           'given when a group name is given')

        if self.train_prog is not None:
            try:
                if self.dept is not None:
                    self.train_prog = bm.TrainingProgramme.objects.get(abbrev=self.train_prog,
                                                                       department=self.dept)
                else:
                    self.train_prog = bm.TrainingProgramme.objects.get(
                        abbrev=self.train_prog)
            except bm.TrainingProgramme.DoesNotExist:
                raise exceptions.NotAcceptable(
                    detail='No such training programme')
            except MultipleObjectsReturned:
                raise exceptions.NotAcceptable(
                    detail='Multiple training programme with this name')

        if group_name is not None:
            try:
                declared_group = bm.StructuralGroup.objects.get(
                    name=group_name, train_prog=self.train_prog)
                self.groups = {declared_group}
                if lineage:
                    self.groups |= declared_group.ancestor_groups()
            except bm.StructuralGroup.DoesNotExist:
                raise exceptions.NotAcceptable(detail='No such group')
            except:
                raise exceptions.NotAcceptable(detail='Issue with the group')
            queryset = queryset.filter(course__groups__in=self.groups)
        else:
            if self.train_prog is not None:
                queryset = queryset.filter(
                    course__groups__train_prog=self.train_prog)

        if group_name is None and self.train_prog is None:
            if self.dept is None:
                if self.tutor is None:
                    raise exceptions.NotAcceptable(
                        detail='You should either a group and a training programme, or a tutor, or a department')
            else:
                queryset = queryset.filter(
                    course__module__train_prog__department=self.dept)
            if self.tutor is not None:
                queryset = queryset.filter(
                    Q(tutor=self.tutor) | Q(course__supp_tutor=self.tutor))

        return queryset

    def get_serializer_class(self):
        # get the department
        if self.dept is None:
            if self.tutor is not None:
                for d in self.tutor.departments.all():
                    uds = pm.UserDepartmentSettings.objects.get(department=d,
                                                                user=self.tutor)
                    if uds.is_main:
                        self.dept = uds.department
                        break

                # no primary department
                if self.dept is None:
                    self.dept = self.tutor.departments.first()
            else:
                self.dept = list(self.groups)[0].train_prog.department
        if self.dept.mode.cosmo:
            return serializers.ScheduledCoursesCosmoSerializer
        else:
            return serializers.ScheduledCoursesSerializer


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          week_param(),
                          year_param(),
                          dept_param(),
                          work_copy_param()
                      ])
                  )
class UnscheduledCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the unscheduled courses

    Result can be filtered as wanted with week, year, work_copy and department fields.
    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.UnscheduledCoursesSerializer

    def get_queryset(self):
        # Creating querysets of all courses and all scheduled courses
        queryset_course = bm.Course.objects.all()
        queryset_sc = bm.ScheduledCourse.objects.all()

        # Getting filters from the URL params (?param1=...&param2=...&...)
        year = self.request.query_params.get('year', None)
        week = self.request.query_params.get('week', None)
        work_copy = self.request.query_params.get('work_copy', 0)
        department = self.request.query_params.get('dept', None)

        # Filtering different querysets
        if year is not None:
            queryset_course = queryset_course.filter(week__year=year)

        if week is not None:
            queryset_course = queryset_course.filter(week__nb=week)

        queryset_sc = queryset_sc.filter(work_copy=work_copy)
        if department is not None:
            queryset_course = queryset_course.filter(
                module__train_prog__department__abbrev=department)
            queryset_sc = queryset_sc.filter(
                course__module__train_prog__department__abbrev=department)

        # Getting courses values of ScheduledCourse objects
        queryset_sc = queryset_sc.values('course')

        # Finding unscheduled courses
        queryset = queryset_course.exclude(pk__in=queryset_sc)

        return queryset


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[week_param(), year_param(), dept_param()])
                  )
class AvailabilitiesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the availabilities of the tutors.

    Result can be filtered as wanted with week, year and department fields.
    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.AvailabilitiesSerializer

    def get_queryset(self):
        # Getting all the wanted data
        qs = bm.UserPreference.objects.all()

        # Getting all the filters
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)
        dept = self.request.query_params.get('dept', None)

        # Filtering
        if week is not None:
            qs = qs.filter(week__nb=week)
        if year is not None:
            qs = qs.filter(week__year=year)
        if dept is not None:
            qs = qs.filter(user__departments__abbrev=dept)

        return qs


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          openapi.Parameter('course_type',
                                            openapi.IN_QUERY,
                                            description="Type of course",
                                            type=openapi.TYPE_STRING),
                          openapi.Parameter('train_prog',
                                            openapi.IN_QUERY,
                                            description="Training Program",
                                            type=openapi.TYPE_STRING),
                          dept_param()
                      ])
                  )
class CourseTypeDefaultWeekViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the Preferences of a given course type in a training program

    Result can be filtered as wanted with the training program and the course type
    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.CourseTypeDefaultWeekSerializer

    def get_queryset(self):
        # Getting the wanted data
        qs = bm.CoursePreference.objects.filter(week__isnull=True)

        # Getting all the filters
        train_prog = self.request.query_params.get('train_prog', None)
        course_type = self.request.query_params.get('course_type', None)
        department = self.request.query_params.get('dept', None)

        # Filtering
        if department is not None:
            qs = qs.select_related('train_prog__department')\
                   .filter(train_prog__department__abbrev=department)
        if train_prog is not None:
            qs = qs.filter(train_prog__abbrev=train_prog)
        if course_type is not None:
            qs = qs.filter(course_type__name=course_type)
        return qs.select_related('course_type', 'train_prog')


class AllVersionsFilterSet(filters.FilterSet):
    permission_classes = [IsAdminOrReadOnly]
    dept = filters.CharFilter(field_name='department__abbrev')

    class Meta:
        model = bm.EdtVersion
        fields = ['dept']


class AllVersionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the versions of the Scheduler

    Result can be filtered as wanted with the department
    by using the function AllVersionsFilterSet
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.EdtVersion.objects.all()
    serializer_class = serializers.AllVersionsSerializer
    filter_class = AllVersionsFilterSet


class DepartmentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the departments

    Can be filtered as wanted with every field of a Department object.
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.Department.objects.all()
    serializer_class = serializers.DepartmentAbbrevSerializer

    filterset_fields = '__all__'


class TutorCoursesFilterSet(filters.FilterSet):
    tutor_name = filters.CharFilter(field_name='user__departments__train_prog__module__module__tutor__username',
                                    required=True)
    year = filters.CharFilter(
        field_name='user__departments__train_prog__module__module__year')
    week = filters.CharFilter(
        field_name='user__departments__train_prog__module__module__week')
    dept = filters.CharFilter(field_name='user__departments__abbrev')

    class Meta:
        model = pm.UserDepartmentSettings
        fields = ['tutor_name', 'year', 'week', 'dept']


class TutorCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the courses of a tutor

    Result needs to be filtered by the username of a tutor.
    Filtering is also possible with week, department and year.
    """
    permission_classes = [IsAdminOrReadOnly]

    serializer_class = serializers.TutorCourses_Serializer
    queryset = pm.UserDepartmentSettings.objects.all()
    filter_class = TutorCoursesFilterSet


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[week_param(), year_param(), user_param(required=True),
                                         dept_param(required=True)])
                  )
class ExtraSchedCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see all the Scheduled courses of a tutor in an other department

    Result can be filtered with year and week
    """
    permission_classes = [IsAdminOrReadOnly]

    serializer_class = serializers.ExtraScheduledCoursesSerializer
    permission_classes = [IsTutorOrReadOnly]

    def get_queryset(self):
        qs_esc = bm.ScheduledCourse.objects.all()
        # Getting all the filters
        user = self.request.query_params.get('username', None)
        dept = self.request.query_params.get('dept', None)
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)

        # Filtering
        if user is None:
            return None
        if dept is None:
            return None

        if week is not None:
            qs_esc = qs_esc.filter(course__week__nb=week)
        if year is not None:
            qs_esc = qs_esc.filter(course__week__year=year)

        # Getting all the needed data

        return qs_esc.filter(course__tutor__username=user)\
                     .exclude(course__module__train_prog__department__abbrev=dept)\
                     .select_related('course__tutor',
                                     'course__type__department',
                                     'course__module__train_prog__department')


class BKNewsFilterSet(filters.FilterSet):
    permission_classes = [IsTutorOrReadOnly]
    dept = filters.CharFilter(field_name='department__abbrev', required=True)
    # makes the fields required
    week = filters.NumberFilter(field_name='week', required=True)
    year = filters.NumberFilter(field_name='year', required=True)

    class Meta:
        model = dwm.BreakingNews
        fields = ['dept', 'week', 'year']


class BKNewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the BKNews

    Result needs to be filtered by the department,the week and the year.
    """
    permission_classes = [IsAdminOrReadOnly]

    queryset = dwm.BreakingNews.objects.all()
    serializer_class = serializers.BKNewsSerializer
    filter_class = BKNewsFilterSet


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[week_param(required=True),
                                         year_param(required=True),
                                         dept_param(required=True)]),

                  )
class UnavailableRoomViewSet(viewsets.ViewSet):
    """
    Allow user to search for unavailable rooms for a given year, week and department

    Each result contains room name, day, start_time, duration, and value (unavailable => 0)
    """
    permission_classes = [IsAdminOrReadOnly]

    def list(self, req, format=None):

        try:
            week = int(req.query_params.get('week'))
            year = int(req.query_params.get('year'))
            department = req.query_params.get('dept')
            if department == 'None':
                department = None
        except ValueError:
            return HttpResponse("KO")

        # ----------------
        # To be done later
        # ----------------
        #
        # cache_key = get_key_unavailable_rooms(department.abbrev, week)
        # cached = cache.get(cache_key)
        # if cached is not None:
        #     return cached

        dataset_room_preference = bm.RoomPreference.objects.filter(room__departments__abbrev=department,
                                                                   week__nb=week,
                                                                   week__year=year,
                                                                   value=0)
        flop_week = bm.Week.objects.get(nb=week, year=year)
        date_of_the_week = [flopday_to_date(Day(week=flop_week, day=d)) for d in days_list]
        dataset_room_reservations = rrm.RoomReservation.objects.filter(room__departments__abbrev=department,
                                                                       date__in=date_of_the_week)

        # cache.set(cache_key, response)7
        res_pref = [{"room": d.room.name,
                     "day": d.day,
                     "start_time": d.start_time,
                     "duration": d.duration,
                     "value": d.value}
                    for d in dataset_room_preference]
        res_reservations = [{"room": d.room.name,
                             "day": days_list[d.date.isocalendar()[2]-1],
                             "start_time": time_to_floptime(d.start_time),
                             "duration": d.duration,
                             "value": 0}
                            for d in dataset_room_reservations]

        return Response(res_pref + res_reservations)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[dept_param(required=True)]),

                  )
class ConstraintsQueriesViewSet(viewsets.ViewSet):
    """
    Return course type constraints for a given department
    """
    permission_classes = [IsAdminOrReadOnly]

    def list(self, req):
        try:
            department = req.query_params.get('dept')
            if department == 'None':
                department = None
        except ValueError:
            return HttpResponse("KO")

        constraints = queries.get_coursetype_constraints(department)
        return JsonResponse(constraints, safe=False)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          week_param(required=True),
                          year_param(required=True),
                          dept_param()
                      ]
                  ),
                  )
class WeekDaysViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def list(self, req):
        week = int(req.query_params.get('week'))
        year = int(req.query_params.get('year'))
        department = req.query_params.get('dept', None)
        if department is not None:
            try:
                department = bm.Department.objects.get(abbrev=department)
            except bm.Department.DoesNotExist:
                raise exceptions.NotFound(detail='Department not found')
        data = weeks.num_all_days(year, week, department)
        return JsonResponse(data, safe=False)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class IDTutorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see the ID and name of every Tutor

    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.IDTutorSerializer

    def get_queryset(self):
        queryset = pm.Tutor.objects.all()

        dept = self.request.query_params.get('dept', None)

        if(dept is not None):
            queryset = queryset.filter(departments__abbrev=dept)

        return(queryset)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class IDTrainProgViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see the ID, abbreviation and name of every TrainingProgramme

    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.IDTrainProgSerializer

    def get_queryset(self):
        queryset = bm.TrainingProgramme.objects.all()

        dept = self.request.query_params.get('dept', None)

        if(dept is not None):
            queryset = queryset.filter(department__abbrev=dept)

        return(queryset)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class IDModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see the ID, abbreviation and name of every Module

    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.IDModuleSerializer

    def get_queryset(self):
        queryset = bm.Module.objects.all()
        dept = self.request.query_params.get('dept', None)

        if(dept is not None):
            queryset = queryset.filter(train_prog__department__abbrev=dept)

        return(queryset)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class IDCourseTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see the ID and name of every CourseType

    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.IDCourseTypeSerializer

    def get_queryset(self):
        queryset = bm.CourseType.objects.all()
        dept = self.request.query_params.get('dept', None)

        if(dept is not None):
            queryset = queryset.filter(department__abbrev=dept)

        return(queryset)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class IDGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see the ID and name of every Group

    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.IDGroupSerializer

    def get_queryset(self):
        queryset = bm.StructuralGroup.objects.all()
        dept = self.request.query_params.get('dept', None)

        if(dept is not None):
            queryset = queryset.filter(train_prog__department__abbrev=dept)

        return(queryset)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class IDGroupTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see the ID and name of every GroupType

    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.IDGroupTypeSerializer

    def get_queryset(self):
        queryset = bm.GroupType.objects.all()
        dept = self.request.query_params.get('dept', None)

        if(dept is not None):
            queryset = queryset.filter(department__abbrev=dept)

        return(queryset)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class IDRoomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see the ID and name of every Room

    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.IDRoomSerializer

    def get_queryset(self):
        queryset = bm.Room.objects.all()
        dept = self.request.query_params.get('dept', None)

        if(dept is not None):
            queryset = queryset.filter(departments__abbrev=dept)

        return(queryset)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class IDRoomTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to see the ID and name of every RoomType

    """
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.IDRoomTypeSerializer

    def get_queryset(self):
        queryset = bm.RoomType.objects.all()
        dept = self.request.query_params.get('dept', None)

        if(dept is not None):
            queryset = queryset.filter(department__abbrev=dept)

        return(queryset)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False)
                      ]
                  ),
                  )
class ParameterViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = '__all__'

    def list(self, request):
        data = {}
        data["people"] = {}
        data["base"] = {}
        data["people"]["Tutor"] = list()

        dept = self.request.query_params.get('dept', None)

        base_types = ["TrainingProgramme", "Module",
                      "CourseType", "Group", "GroupType", "Room", "RoomType"]

        qtutor = pm.Tutor.objects.all()

        if(dept is not None):
            qtutor = qtutor.filter(departments__abbrev=dept)

        for object in qtutor:
            serializer = serializers.IDTutorSerializer(object)
            data["people"]["Tutor"].append(serializer.data)

        for typename in base_types:
            model = apps.get_model("base", typename)
            data["base"][typename] = list()
            queryset = model.objects.all()

            if(dept is not None):
                if (typename == "Room"):
                    queryset = queryset.filter(departments__abbrev=dept)

                if (typename in ["Group", "Module"]):
                    queryset = queryset.filter(
                        train_prog__department__abbrev=dept)

                if (typename in ["TrainingProgramme", "CourseType", "GroupType", "RoomType"]):
                    queryset = queryset.filter(department__abbrev=dept)

            for object in queryset:
                serializer = serializers.IDRoomSerializer(object)
                data["base"][typename].append(serializer.data)

        return Response(data)
