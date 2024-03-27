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

from random import randint

import django_filters.rest_framework as filters
from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response

import base.models as bm
import base.queries as queries
import displayweb.models as dwm
import quote.models as qm
import TTapp.models as tm
from api import serializers
from api.permissions import IsAdminOrReadOnly, IsTutorOrReadOnly
from api.shared.params import dept_param, week_param, year_param

# ----------
# -- QUOTE -
# ----------


class QuoteTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the quote types.

    Can be filtered as wanted with every field of a QuoteType object.
    """

    permission_classes = [IsAdminOrReadOnly]
    queryset = qm.QuoteType.objects.all()
    serializer_class = serializers.QuoteTypeSerializer

    filterset_fields = "__all__"


class QuoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the quotes.

    Can be filtered as wanted with every field of a Quote object.
    """

    queryset = qm.Quote.objects.all()
    serializer_class = serializers.QuoteSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = "__all__"


class RandomQuoteViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, format=None):
        """
        Return a random quote
        """
        ids = qm.Quote.objects.filter(status=qm.Quote.ACCEPTED).values_list(
            "id", flat=True
        )
        nb_quotes = len(ids)
        if nb_quotes > 0:
            chosen_id = ids[randint(0, nb_quotes - 1)] if nb_quotes > 0 else -1
            return Response(str(qm.Quote.objects.get(id=chosen_id)))
        return Response("")

        permission_classes = [IsAdminOrReadOnly]


# ---------------
# -- DISPLAYWEB -
# ---------------


class BreakingNewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the breaking news.

    Can be filtered as wanted with every field of a BreakingNews object.
    """

    permission_classes = [IsAdminOrReadOnly]

    queryset = dwm.BreakingNews.objects.all()
    serializer_class = serializers.BreakingNewsSerializer

    filterset_fields = "__all__"


class ModuleDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the module displays(the color of the background and the txt)

    Can be filtered as wanted with every field of a ModuleDisplay object.
    """

    permission_classes = [IsAdminOrReadOnly]

    queryset = dwm.ModuleDisplay.objects.all()
    serializer_class = serializers.ModuleDisplaysSerializer

    filterset_fields = "__all__"


class TrainingProgrammeDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the training programme displays.

    Can be filtered as wanted with every field of a TrainingProgrammeDisplay object.
    """

    permission_classes = [IsAdminOrReadOnly]
    queryset = dwm.TrainingProgrammeDisplay.objects.all()
    serializer_class = serializers.TrainingProgrammeDisplaysSerializer

    filterset_fields = "__all__"


class GroupDisplaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the group displays.

    Can be filtered as wanted with every field of a GroupDisplay object.
    """

    permission_classes = [IsAdminOrReadOnly]

    queryset = dwm.GroupDisplay.objects.all()
    serializer_class = serializers.GroupDisplaysSerializer
    filterset_fields = "__all__"


# --------------------
# --- PERIOD-INFOS  ----
# --------------------


def pref_requirements(department, tutor, period_id):
    """
    TODO new-time : Il faut prendre en compte les préférences par défaut...
    Return a pair (filled, required): number of preferences
    that have been proposed VS required number of prefs, according
    to local policy
    """
    period = bm.SchedulingPeriod.objects.get(id=period_id)
    courses_time = sum(
        c.duration
        for c in bm.Course.objects.filter(
            Q(tutor=tutor) | Q(supp_tutor=tutor), week=period
        )
    )
    week_av = bm.UserAvailability.objects.filter(
        user=tutor, week=period, day__in=queries.get_working_days(department)
    )
    if not week_av.exists():
        week_av = bm.UserAvailability.objects.filter(
            user=tutor, week=None, day__in=queries.get_working_days(department)
        )

    # Exclude Holidays
    holidays_query = bm.Holiday.objects.filter(week=period)
    if holidays_query.exists():
        holidays = [h.day for h in holidays_query]
        week_av = week_av.exclude(day__in=holidays)

    # FIXME New-time
    # Exclude NoTutorCourseOnDay
    tutor_no_course_on_day_query = tm.NoTutorCourseOnDay.objects.filter(
        Q(tutors=tutor) | Q(tutors__isnull=True),
        Q(weeks=week) | Q(weeks__isnull=True),
        weight=None,
    )
    if tutor_no_course_on_day_query.exists():
        for tncod in tutor_no_course_on_day_query:
            if tncod.fampm_period == tm.NoTutorCourseOnDay.FULL_DAY:
                week_av = week_av.exclude(day=tncod.weekday)
            elif tncod.fampm_period == tm.NoTutorCourseOnDay.AM:
                week_av = week_av.exclude(
                    day=tncod.weekday,
                    start_time__lt=department.timegeneralsettings.lunch_break_start_time,
                )
            elif tncod.fampm_period == tm.NoTutorCourseOnDay.PM:
                week_av = week_av.exclude(
                    day=tncod.weekday,
                    start_time__gte=department.timegeneralsettings.lunch_break_end_time,
                )

    filled = sum(
        a.duration
        for a in week_av.filter(
            value__gte=1, day__in=queries.get_working_days(department)
        )
    )

    # Exclude lunch break TODO
    tutor_lunch_break_query = tm.TutorsLunchBreak.objects.filter(
        Q(tutors=tutor) | Q(tutors__isnull=True),
        Q(weeks=period) | Q(weeks__isnull=True),
    )

    # END FIXME New-time

    return filled, courses_time


class WeekInfoViewSet(viewsets.ViewSet):
    """
    Aggregated infos of a given week

    Version number, required number of available slots,
    proposed number of available slots
    (not cached)
    """

    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        parameters=[
            week_param(required=True),
            year_param(required=True),
            dept_param(required=True),
        ]
    )
    def list(self, request, format=None):
        period_id = int(request.query_params.get("period_id"))

        try:
            department = bm.Department.objects.get(
                abbrev=request.query_params.get("dept")
            )
        except bm.Department.DoesNotExist as exc:
            raise DepartmentUnknown from exc

        version = 0
        for dept in bm.Department.objects.all():
            version += queries.get_edt_version(dept, period_id, create=True)

        proposed_pref, required_pref = (
            pref_requirements(department, request.user, period_id)
            if request.user.is_authenticated
            else (-1, -1)
        )

        try:
            regen = str(
                bm.Regen.objects.get(department=department, period__id=period_id)
            )
        except bm.Regen.DoesNotExist:
            regen = "I"

        return Response(
            {
                "version": version,
                "proposed_pref": proposed_pref,
                "required_pref": required_pref,
                "regen": regen,
            }
        )


# -------------------
# --- Exceptions ----
# -------------------


class DepartmentUnknown(APIException):
    status_code = 400
    default_detail = "There is no department with this abbreviated name."
    default_code = "department_unknown"
