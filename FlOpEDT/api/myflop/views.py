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

import datetime as dt

from django.db.models import Case, Count, F, Q, When
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.exceptions import APIException, NotAcceptable
from rest_framework.response import Response

from api.myflop.serializers import (
    DailyVolumeSerializer,
    DuplicateSerializer,
    RoomDailyVolumeSerializer,
    ScheduledCoursePaySerializer,
    VolumeAgrege,
)
from api.permissions import IsTutorOrReadOnly
from api.shared.params import dept_param
from base.models import (
    Department,
    Room,
    ScheduledCourse,
    TrainingProgramme,
)
from people.models import Tutor


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            dept_param(required=True),
            openapi.Parameter(
                "from",
                openapi.IN_QUERY,
                description="initial date",
                type=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                "to",
                openapi.IN_QUERY,
                description="final date",
                type=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                "train_prog",
                openapi.IN_QUERY,
                description="training program abbreviation",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "for",
                openapi.IN_QUERY,
                description="f : full staff ; s : supply staff" " ; a : all",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "with_contunuing_training",
                openapi.IN_QUERY,
                description="distinguish continuing training ?",
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
        ]
    ),
)
class PayViewSet(viewsets.ViewSet):
    """
    Gestion de la paye
    """

    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):
        param_exception = NotAcceptable(
            detail=f"Usage : ?from=YYYY-MM-DD&to=YYYY-MM-DD"
            f"&for=f_or_s_or_a where "
            f"f : full staff ; s : supply staff ; a : all"
        )

        wanted_param = ["from", "to", "for"]
        supp_filters = {}

        # check that all parameters are given
        for param in wanted_param:
            if param not in request.GET:
                raise param_exception

        dept = self.request.query_params.get("dept", None)
        if dept is not None:
            try:
                dept = Department.objects.get(abbrev=dept)
            except Department.DoesNotExist:
                raise APIException(detail="Unknown department")

        # clean dates
        from_date = dt.date.fromisoformat(self.request.query_params.get("from"))
        to_date = dt.date.fromisoformat(self.request.query_params.get("to"))

        # clean training programme
        train_prog = self.request.query_params.get("train_prog", None)
        if train_prog is not None:
            try:
                train_prog = TrainingProgramme.objects.get(
                    department=dept, abbrev=train_prog
                )
                supp_filters["course__module__train_prog"] = train_prog
            except TrainingProgramme.DoesNotExist:
                raise APIException(detail="Unknown training programme")

        # clean status
        status_dict = {
            "f": [Tutor.FULL_STAFF],
            "s": [Tutor.SUPP_STAFF],
            "a": [Tutor.FULL_STAFF, Tutor.SUPP_STAFF],
        }
        status_set = status_dict[request.GET.get("for")]

        # clean continuing training
        with_continuing_training = self.request.query_params.get(
            "with_contunuing_training", False
        )

        volumes = (
            ScheduledCourse.objects.select_related("course__module__train_prog")
            .filter(
                date__gte=from_date,
                date__lte=to_date,
                course__type__department=dept,
                verion__major=0,
                tutor__status__in=status_set,
                **supp_filters,
            )
            .annotate(
                department=F("course__type__department__abbrev"),
                course_type_id=F("course__type__id"),
                # if pay_module is not null, consider it, else consider module
                module_id=Case(
                    When(
                        course__pay_module__isnull=False,
                        then=F("course__pay_module__id"),
                    ),
                    When(course__pay_module__isnull=True, then=F("course__module__id")),
                ),
                module_ppn=Case(
                    When(
                        course__pay_module__isnull=False,
                        then=F("course__pay_module__ppn"),
                    ),
                    When(
                        course__pay_module__isnull=True, then=F("course__module__ppn")
                    ),
                ),
                module__name=Case(
                    When(
                        course__pay_module__isnull=False,
                        then=F("course__pay_module__name"),
                    ),
                    When(
                        course__pay_module__isnull=True, then=F("course__module__name")
                    ),
                ),
                train_prog_abbrev=F("course__groups__train_prog__abbrev"),
                group_name=F("course__groups__name"),
                course_type_name=F("course__type__name"),
                type_id=F("course__type__id"),
                tutor_username=F("tutor__username"),
                tutor_first_name=F("tutor__first_name"),
                tutor_last_name=F("tutor__last_name"),
            )
            .values(
                "id",
                "department",
                "module_id",
                "module_ppn",
                "tutor__id",
                "course_type_id",
                "tutor__username",
                "course_type_name",
                "type_id",
                "module_name",
                "tutor_username",
                "tutor_first_name",
                "tutor_last_name",
                "train_prog_abbrev",
                "group_name",
                "duration",
                "pay_duration",
            )
            .annotate(slots_nb=Count("id"))
            .order_by("module_id", "tutor__id", "course_type_id")
        )

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


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            dept_param(required=False),
            openapi.Parameter(
                "from_month",
                openapi.IN_QUERY,
                description="from_month",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "to_month",
                openapi.IN_QUERY,
                description="to_month",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
                description="year",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "tutor",
                openapi.IN_QUERY,
                description="tutor username",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ]
    ),
)
class MonthlyVolumeByDayViewSet(viewsets.ViewSet):
    """
    Volume de cours par jour pour un intervenant
    """

    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):
        param_exception = NotAcceptable(detail=f"Les champs annee et prof sont requis")
        wanted_param = ["year", "tutor"]

        # check that all parameters are given
        for param in wanted_param:
            if param not in request.GET:
                raise param_exception

        dept = self.request.query_params.get("dept", None)
        if dept is not None:
            try:
                dept = Department.objects.get(abbrev=dept)
            except Department.DoesNotExist:
                raise APIException(detail="Unknown department")

        tutor = self.request.query_params.get("tutor", None)
        if tutor is not None:
            try:
                tutor = Tutor.objects.get(username=tutor)
            except Tutor.DoesNotExist:
                raise APIException(detail="Unknown tutor")

        year = int(self.request.query_params.get("year"))
        from_month = int(self.request.query_params.get("from_month", 1))
        to_month = int(self.request.query_params.get("to_month", 12))

        day_volumes_list = []

        sched_courses = scheduled_courses_of_the_month(
            year=year,
            from_month=from_month,
            to_month=to_month,
            department=dept,
            tutor=tutor,
        )
        for dayschedcourse in sched_courses.distinct("date"):
            sched_course_date = dayschedcourse.date
            day_scheduled_courses = sched_courses.filter(date=sched_course_date)
            tds = day_scheduled_courses.filter(course__type__name="TD")
            tps = day_scheduled_courses.filter(course__type__name="TP")
            other = day_scheduled_courses.exclude(course__type__name__in=["TD", "TP"])

            other = sum(sc.pay_duration for sc in other).seconds() // 60
            td = sum(sc.pay_duration for sc in tds).seconds() // 60
            tp = sum(sc.pay_duration for sc in tps).seconds() // 60

            day_volume = {
                "month": sched_course_date.month,
                "date": sched_course_date.isoformat(),
                "other": other,
                "td": td,
                "tp": tp,
            }

            day_volumes_list.append(day_volume)
            day_volumes_list.sort(key=lambda x: x["date"])
        serializer = DailyVolumeSerializer(day_volumes_list, many=True)
        return Response(serializer.data)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            dept_param(required=True),
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
                description="year",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "from_month",
                openapi.IN_QUERY,
                description="from_month",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "to_month",
                openapi.IN_QUERY,
                description="to_month",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "tutor",
                openapi.IN_QUERY,
                description="tutor username",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ]
    ),
)
class MonthlyByDayDuplicatesViewSet(viewsets.ViewSet):
    """
    Duplicates of scheduled courses by day
    """

    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):
        dept = self.request.query_params.get("dept")
        try:
            dept = Department.objects.get(abbrev=dept)
        except Department.DoesNotExist:
            raise APIException(detail="Unknown department")

        tutor = self.request.query_params.get("tutor", None)
        if tutor is not None:
            try:
                tutor = Tutor.objects.get(username=tutor)
            except Tutor.DoesNotExist:
                raise APIException(detail="Unknown tutor")

        year = int(self.request.query_params.get("year"))
        from_month = int(self.request.query_params.get("from_month", 1))
        to_month = int(self.request.query_params.get("to_month", 12))

        duplicates_list = []

        duplicates_sched_courses = duplicates_scheduled_courses_of_the_month(
            year=year,
            from_month=from_month,
            to_month=to_month,
            department=dept,
            tutor=tutor,
        )

        for key in duplicates_sched_courses:
            duplicate_tutor, date, course_type, in_day_start_time = key
            day_duplicates = {
                "tutor": duplicate_tutor.username,
                "date": date.isoformat(),
                "type": course_type,
                "time": in_day_start_time.strftime("%H:%M"),
                "nb": duplicates_sched_courses[key],
            }

            duplicates_list.append(day_duplicates)
            duplicates_list.sort(key=lambda x: (x["tutor"], x["date"], x["time"]))
        serializer = DuplicateSerializer(duplicates_list, many=True)
        return Response(serializer.data)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            dept_param(required=False),
            openapi.Parameter(
                "from_month",
                openapi.IN_QUERY,
                description="from_month",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "to_month",
                openapi.IN_QUERY,
                description="to_month",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
                description="year",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "room",
                openapi.IN_QUERY,
                description="room_name",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ]
    ),
)
class RoomMonthlyVolumeByDayViewSet(viewsets.ViewSet):
    """
    Volume de cours par jour pour une salle
    """

    permission_classes = [IsTutorOrReadOnly]

    def list(self, request):
        param_exception = NotAcceptable(detail=f"Les champs year et room sont requis")
        wanted_param = ["month", "year", "room"]

        # check that all parameters are given
        for param in wanted_param:
            if param not in request.GET:
                raise param_exception

        dept = self.request.query_params.get("dept", None)
        if dept is not None:
            try:
                dept = Department.objects.get(abbrev=dept)
            except Department.DoesNotExist:
                raise APIException(detail="Unknown department")

        room = self.request.query_params.get("room", None)
        if room is not None:
            try:
                room = Room.objects.get(name=room)
            except Tutor.DoesNotExist:
                raise APIException(detail="Unknown tutor")

        year = int(self.request.query_params.get("year"))
        from_month = int(self.request.query_params.get("from_month", 1))
        to_month = int(self.request.query_params.get("to_month", 12))

        day_volumes_list = []

        sched_courses = scheduled_courses_of_the_month(
            year=year,
            from_month=from_month,
            to_month=to_month,
            department=dept,
            room=room,
        )
        for dayschedcourse in sched_courses.distinct("date"):
            date = dayschedcourse.date
            day_scheduled_courses = sched_courses.filter(date=date)
            volume = (
                sum(sc.pay_duration for sc in day_scheduled_courses).seconds() // 60
            )
            day_volume = {
                "date": date.isoformat(),
                "volume": volume,
            }
            day_volumes_list.append(day_volume)
            day_volumes_list.sort(key=lambda x: x["date"])
        serializer = RoomDailyVolumeSerializer(day_volumes_list, many=True)
        return Response(serializer.data)


def scheduled_courses_of_the_month(
    year, from_month=None, to_month=None, department=None, tutor=None, room=None
):
    if from_month is None:
        start_datetime = datetime.datetime(year, 1, 1)
    else:
        start_datetime = datetime.datetime(year, from_month, 1)

    if to_month is None:
        end_datetime = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(1)
    elif to_month == 12:
        end_datetime = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(1)
    else:
        end_datetime = datetime.datetime(year, to_month + 1, 1) - datetime.timedelta(1)

    relevant_scheduled_courses = ScheduledCourse.objects.filter(version__major=0)
    if department is not None:
        relevant_scheduled_courses = relevant_scheduled_courses.filter(
            course__type__department=department
        )
    if tutor is not None:
        relevant_scheduled_courses = relevant_scheduled_courses.filter(tutor=tutor)
    if room is not None:
        relevant_scheduled_courses = relevant_scheduled_courses.filter(
            room__in=room.and_overrooms()
        )
    relevant_scheduled_courses = relevant_scheduled_courses.filter(
        start_time__gte=start_datetime, start_time__lt=end_datetime
    )
    return relevant_scheduled_courses


def duplicates_scheduled_courses_of_the_month(
    year, from_month=None, to_month=None, department=None, tutor=None
):
    result_dict = {}
    sorted_scheduled_courses = scheduled_courses_of_the_month(
        year, from_month, to_month, department, tutor
    )
    for specimen in sorted_scheduled_courses.distinct("start_time", "tutor"):
        if specimen.tutor is not None:
            count = sorted_scheduled_courses.filter(
                start_time=specimen.start_time,
                tutor=specimen.tutor,
            ).count()
            if count > 1:
                result_dict[
                    specimen.tutor,
                    specimen.date,
                    specimen.course.type.name,
                    specimen.in_day_start_time,
                ] = count
    return result_dict
