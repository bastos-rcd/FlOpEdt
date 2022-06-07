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
from django.db.models import Count, F, Sum, Q

from people.models import Tutor
from base.models import ScheduledCourse, Department, TrainingProgramme, Week

from api.permissions import IsTutorOrReadOnly
from api.shared.params import dept_param
from api.myflop.serializers import VolumeAgrege, ScheduledCoursePaySerializer

import datetime
from base.timing import days_list


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
                        course__tutor__status__in=status_set,
                        **supp_filters)\
                .annotate(
                    department=F('course__type__department__abbrev'),
                    course_type_id=F('course__type__id'),
                    module_id=F('course__module__id'),
                    module_ppn=F('course__module__ppn'),
                    train_prog_abbrev=F('course__groups__train_prog__abbrev'),
                    group_name=F('course__groups__name'),
                    type_cours=F('course__type__name'),
                    type_id=F('course__type__id'),
                    nom_matiere=F('course__module__name'),
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


def scheduled_courses_of_the_month(department, year, month):
    start_month = datetime.datetime(year, month, 1)
    start_year, start_week_nb, start_day = start_month.isocalendar()
    if month < 12:
        end_month = datetime.datetime(year, month+1, 1) - datetime.timedelta(1)
    else:
        end_month = datetime.datetime(year+1, 1, 1) - datetime.timedelta(1)
    end_year, end_week_nb, end_day = end_month.isocalendar()
    start_week = Week.objects.get(nb=start_week_nb, year=start_year)
    end_week = Week.objects.get(nb=end_week_nb, year=end_year)
    if start_year == end_year:
        intermediate_weeks = Week.objects.filter(year=start_year, nb__gt=start_week_nb, nb__lt=end_week_nb)
    else:
        intermediate_weeks = Week.objects.filter(Q(year=start_year, nb__gt=start_week_nb)
                                                 | Q(year=end_year, nb__lt=end_week_nb))
    relevant_scheduled_courses = ScheduledCourse.objects.filter(course__type__department=department, work_copy=0)
    query = Q(course__week__in=intermediate_weeks) | \
            Q(course__week=start_week, day__in=days_list[start_day-1:]) | \
            Q(course__week=end_week, day__in=days_list[:end_day])

    relevant_scheduled_courses = \
        relevant_scheduled_courses.filter(query).exclude(course__week=start_week, day=days_list[start_day-1],
                                                         start_time=0)
    return relevant_scheduled_courses
