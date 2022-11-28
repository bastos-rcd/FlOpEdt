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

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, APIException

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.utils.decorators import method_decorator
from django.db.models import Count, F, Sum, Q, Case, When

from people.models import Tutor
from base.models import ScheduledCourse, Department, TrainingProgramme, Week, Room

from api.permissions import IsTutorOrReadOnly
from api.shared.params import dept_param
from api.myflop.serializers import VolumeAgrege, ScheduledCoursePaySerializer, DailyVolumeSerializer, \
    RoomDailyVolumeSerializer

import datetime
from base.timing import days_list, flopday_to_date, Day


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=True),
                          openapi.Parameter('de_semaine',
                                            openapi.IN_QUERY,
                                            description="semaine initiale",
                                            type=openapi.TYPE_INTEGER,
                                            required=True),
                          openapi.Parameter('de_annee',
                                            openapi.IN_QUERY,
                                            description="année initiale",
                                            type=openapi.TYPE_INTEGER,
                                            required=True),
                          openapi.Parameter('a_semaine',
                                            openapi.IN_QUERY,
                                            description="semaine finale",
                                            type=openapi.TYPE_INTEGER,
                                            required=True),
                          openapi.Parameter('a_annee',
                                            openapi.IN_QUERY,
                                            description="année finale",
                                            type=openapi.TYPE_INTEGER,
                                            required=True),
                          openapi.Parameter('promo',
                                            openapi.IN_QUERY,
                                            description="abbréviation de la promo",
                                            type=openapi.TYPE_STRING,
                                            required=False),
                          openapi.Parameter('pour',
                                            openapi.IN_QUERY,
                                            description=\
                                            "p : permanent·e·s ; v : vacataires"
                                            " ; t : tou·te·s",
                                            type=openapi.TYPE_STRING,
                                            required=True),
                          openapi.Parameter('avec_formation_continue',
                                            openapi.IN_QUERY,
                                            description=\
                                            "distinguer la formation continue?",
                                            type=openapi.TYPE_BOOLEAN,
                                            required=False),
                      ])
                  )
class PayViewSet(viewsets.ViewSet):
    """
    Gestion de la paye
    """
    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):

        param_exception = NotAcceptable(
            detail=f"Usage : ?de_semaine=xx&de_annee=xy"
            f"&a_semaine=yx&a_annee=yy"
            f"&pour=p_ou_v_ou_t où "
            f"p : permanent·e·s ; v : vacataires ; "
            f"t : tou·te·s"
        )

        wanted_param = ['de_semaine', 'de_annee', 'a_semaine', 'a_annee',
                        'pour']
        supp_filters = {}

        # check that all parameters are given
        for param in wanted_param:
            if param not in request.GET:
                raise param_exception

        dept = self.request.query_params.get('dept', None)
        if dept is not None:
            try:
                dept = Department.objects.get(abbrev=dept)
            except Department.DoesNotExist:
                raise APIException(detail='Unknown department')

        # clean week-year parameters
        week_inter = [
            {'year': request.GET.get('de_annee'),
             'min_week':request.GET.get('de_semaine'),
             'max_week':60},
            {'year': request.GET.get('a_annee'),
             'min_week':1,
             'max_week':request.GET.get('a_semaine')}
        ]
        if week_inter[0]['year'] == week_inter[1]['year']:
            week_inter[0]['max_week'] = week_inter[1]['max_week']
            week_inter[1]['max_week'] = 0

        Q_filter_week = \
            Q(course__week__nb__gte=week_inter[0]['min_week'])\
            & Q(course__week__nb__lte=week_inter[0]['max_week'])\
            & Q(course__week__year=week_inter[0]['year'])\
            | \
            Q(course__week__nb__gte=week_inter[1]['min_week'])\
            & Q(course__week__nb__lte=week_inter[1]['max_week'])\
            & Q(course__week__year=week_inter[1]['year'])


        # clean training programme
        train_prog = self.request.query_params.get('promo', None)
        if train_prog is not None:
            try:
                train_prog = TrainingProgramme.objects.get(department=dept,
                                                           abbrev=train_prog)
                supp_filters['train_prog'] = train_prog
            except TrainingProgramme.DoesNotExist:
                raise APIException(detail='Unknown training programme')


        # clean status
        status_dict = {
            'p': [Tutor.FULL_STAFF],
            'v': [Tutor.SUPP_STAFF],
            't': [Tutor.FULL_STAFF, Tutor.SUPP_STAFF]
        }
        status_set = status_dict[request.GET.get('pour')]

        # formation continue
        avec_formation_contine = request.GET.get('avec_formation_continue', None)

        volumes = \
            ScheduledCourse.objects.select_related(
                'course__week',
                'course__module__train_prog')\
                .filter(Q_filter_week,
                        course__module__train_prog__department=dept,
                        work_copy=0,
                        tutor__status__in=status_set,
                        **supp_filters)\
                .annotate(
                    department=F('course__type__department__abbrev'),
                    course_type_id=F('course__type__id'),
                    # if pay_module is not null, consider it, else consider module
                    module_id=Case(
                        When(course__pay_module__isnull=False, then=F('course__pay_module__id')),
                        When(course__pay_module__isnull=True, then=F('course__module__id'))),
                    module_ppn=Case(
                        When(course__pay_module__isnull=False, then=F('course__pay_module__ppn')),
                        When(course__pay_module__isnull=True, then=F('course__module__ppn'))),
                    nom_matiere=Case(
                        When(course__pay_module__isnull=False, then=F('course__pay_module__name')),
                        When(course__pay_module__isnull=True, then=F('course__module__name'))),
                    train_prog_abbrev=F('course__groups__train_prog__abbrev'),
                    group_name=F('course__groups__name'),
                    type_cours=F('course__type__name'),
                    type_id=F('course__type__id'),
                    abbrev_intervenant=F('tutor__username'),
                    prenom_intervenant=F('tutor__first_name'),
                    nom_intervenant=F('tutor__last_name'))\
                .values('id',
                        'department',
                        'module_id',
                        'module_ppn',
                        'tutor__id',
                        'course_type_id',
                        'tutor__username',
                        'nom_matiere',
                        'type_cours',
                        'type_id',
                        'nom_matiere',
                        'abbrev_intervenant',
                        'prenom_intervenant',
                        'nom_intervenant',
                        'train_prog_abbrev',
                        'group_name')\
                .annotate(nb_creneau=Count('id')) \
                .order_by('module_id',
                          'tutor__id',
                          'course_type_id')

        agg_list = []

        if volumes.exists():
            print(volumes[0])
            agg_list.append(VolumeAgrege(volumes[0]))
            agg_list[0].formation_reguliere = 0
            agg_list[0].formation_continue = 0
            prev = agg_list[0]

            for sc in volumes:
                new_agg = prev.add(sc)
                if new_agg is not None:
                    agg_list.append(new_agg)
                    prev = new_agg

        serializer = ScheduledCoursePaySerializer(agg_list, many=True)
        return Response(serializer.data)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False),
                          openapi.Parameter('from_month',
                                            openapi.IN_QUERY,
                                            description="from_month",
                                            type=openapi.TYPE_INTEGER,
                                            required=False),
                          openapi.Parameter('to_month',
                                            openapi.IN_QUERY,
                                            description="to_month",
                                            type=openapi.TYPE_INTEGER,
                                            required=False),
                          openapi.Parameter('year',
                                            openapi.IN_QUERY,
                                            description="year",
                                            type=openapi.TYPE_INTEGER,
                                            required=True),
                          openapi.Parameter('tutor',
                                            openapi.IN_QUERY,
                                            description="tutor username",
                                            type=openapi.TYPE_STRING,
                                            required=True),
                      ])
                  )
class MonthlyVolumeByDayViewSet(viewsets.ViewSet):
    """
    Volume de cours par jour pour un intervenant
    """
    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):
        param_exception = NotAcceptable(
            detail=f"Les champs annee et prof sont requis"
        )
        wanted_param = ['year', 'tutor']

        # check that all parameters are given
        for param in wanted_param:
            if param not in request.GET:
                raise param_exception

        dept = self.request.query_params.get('dept', None)
        if dept is not None:
            try:
                dept = Department.objects.get(abbrev=dept)
            except Department.DoesNotExist:
                raise APIException(detail='Unknown department')

        tutor = self.request.query_params.get('tutor', None)
        if tutor is not None:
            try:
                tutor = Tutor.objects.get(username=tutor)
            except Tutor.DoesNotExist:
                raise APIException(detail='Unknown tutor')

        year = int(self.request.query_params.get('year'))
        from_month = int(self.request.query_params.get('from_month', 1))
        to_month = int(self.request.query_params.get('to_month', 12))

        day_volumes_list = []

        sched_courses = scheduled_courses_of_the_month(year=year, from_month=from_month, to_month=to_month,
                                                       department=dept, tutor=tutor)
        for dayschedcourse in sched_courses.distinct("course__week", "day"):
            week = dayschedcourse.course.week
            week_day = dayschedcourse.day
            day_scheduled_courses = sched_courses.filter(course__week=week, day=week_day)
            tds = day_scheduled_courses.filter(course__type__name='TD')
            tps = day_scheduled_courses.filter(course__type__name='TP')
            other = day_scheduled_courses.exclude(course__type__name__in=['TD', "TP"])

            other = sum(sc.pay_duration for sc in other)/60
            td = sum(sc.pay_duration for sc in tds)/60
            tp = sum(sc.pay_duration for sc in tps)/60

            date = flopday_to_date(Day(week=week, day=week_day))

            day_volume = {
                "month": date.month,
                "date": date.isoformat(),
                "other": other,
                "td": td,
                "tp": tp
            }

            day_volumes_list.append(day_volume)
            day_volumes_list.sort(key=lambda x: x["date"])
        serializer = DailyVolumeSerializer(day_volumes_list, many=True)
        return Response(serializer.data)


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          dept_param(required=False),
                          openapi.Parameter('from_month',
                                            openapi.IN_QUERY,
                                            description="from_month",
                                            type=openapi.TYPE_INTEGER,
                                            required=False),
                          openapi.Parameter('to_month',
                                            openapi.IN_QUERY,
                                            description="to_month",
                                            type=openapi.TYPE_INTEGER,
                                            required=False),
                          openapi.Parameter('year',
                                            openapi.IN_QUERY,
                                            description="year",
                                            type=openapi.TYPE_INTEGER,
                                            required=True),
                          openapi.Parameter('room',
                                            openapi.IN_QUERY,
                                            description="room_name",
                                            type=openapi.TYPE_STRING,
                                            required=True),
                      ])
                  )
class RoomMonthlyVolumeByDayViewSet(viewsets.ViewSet):
    """
    Volume de cours par jour pour une salle
    """
    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):
        param_exception = NotAcceptable(
            detail=f"Les champs year et room sont requis"
        )
        wanted_param = ['month', 'year', 'room']

        # check that all parameters are given
        for param in wanted_param:
            if param not in request.GET:
                raise param_exception

        dept = self.request.query_params.get('dept', None)
        if dept is not None:
            try:
                dept = Department.objects.get(abbrev=dept)
            except Department.DoesNotExist:
                raise APIException(detail='Unknown department')

        room = self.request.query_params.get('room', None)
        if room is not None:
            try:
                room = Room.objects.get(name=room)
            except Tutor.DoesNotExist:
                raise APIException(detail='Unknown tutor')

        year = int(self.request.query_params.get('year'))
        from_month = int(self.request.query_params.get('from_month', 1))
        to_month = int(self.request.query_params.get('to_month', 12))

        day_volumes_list = []

        sched_courses = scheduled_courses_of_the_month(year=year, from_month=from_month, to_month=to_month,
                                                       department=dept, room=room)
        for dayschedcourse in sched_courses.distinct("course__week", "day"):
            week = dayschedcourse.course.week
            week_day = dayschedcourse.day
            day_scheduled_courses = sched_courses.filter(course__week=week, day=week_day)
            volume = sum(sc.pay_duration for sc in day_scheduled_courses)/60

            date = flopday_to_date(Day(week=week, day=week_day))

            day_volume = {
                "date": date.isoformat(),
                "volume": volume,
            }

            day_volumes_list.append(day_volume)
            day_volumes_list.sort(key=lambda x: x["date"])
        serializer = RoomDailyVolumeSerializer(day_volumes_list, many=True)
        return Response(serializer.data)



def scheduled_courses_of_the_month(year, from_month=None, to_month=None, department=None, tutor=None, room=None):
    if from_month is None:
        start_month = datetime.datetime(year, 1, 1)
    else:
        start_month = datetime.datetime(year, from_month, 1)
    start_year, start_week_nb, start_day = start_month.isocalendar()

    if to_month is None:
        end_month = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(1)
    elif to_month == 12:
        end_month = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(1)
    else:
        end_month = datetime.datetime(year, to_month+1, 1) - datetime.timedelta(1)
    end_year, end_week_nb, end_day = end_month.isocalendar()

    start_week = Week.objects.get(nb=start_week_nb, year=start_year)
    end_week = Week.objects.get(nb=end_week_nb, year=end_year)
    if start_year == end_year:
        intermediate_weeks = Week.objects.filter(year=start_year, nb__gt=start_week_nb, nb__lt=end_week_nb)
    else:
        intermediate_weeks = Week.objects.filter(Q(year=start_year, nb__gt=start_week_nb)
                                                 | Q(year=end_year, nb__lt=end_week_nb))
    relevant_scheduled_courses = ScheduledCourse.objects.filter(work_copy=0)
    if department is not None:
        relevant_scheduled_courses = relevant_scheduled_courses.filter(course__type__department=department)
    if tutor is not None:
        relevant_scheduled_courses = relevant_scheduled_courses.filter(tutor=tutor)
    if room is not None:
        relevant_scheduled_courses = relevant_scheduled_courses.filter(room__in=room.and_overrooms())
    query = Q(course__week__in=intermediate_weeks) | \
            Q(course__week=start_week, day__in=days_list[start_day-1:]) | \
            Q(course__week=end_week, day__in=days_list[:end_day])

    relevant_scheduled_courses = \
        relevant_scheduled_courses.filter(query).exclude(course__week=start_week, day=days_list[start_day-1],
                                                         start_time=0)
    return relevant_scheduled_courses
