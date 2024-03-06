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
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework import exceptions

from django.utils.decorators import method_decorator
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

from django.apps import apps

import base.models as bm
import people.models as pm

from . import serializers
from api.shared.params import (
    dept_id_param,
    dept_param,
    from_date_param,
    to_date_param,
    work_copy_param,
    group_param,
    train_prog_param,
    lineage_param,
    tutor_param,
)
from api.permissions import IsAdminOrReadOnly

from base.timing import date_to_flopday, days_list, days_index
import datetime as dt


@extend_schema(
    parameters=[
        from_date_param(required=True),
        to_date_param(required=True),
        work_copy_param(),
        dept_id_param(),
        dept_param(),
        train_prog_param(),
        group_param(),
        lineage_param(),
        tutor_param(),
    ]
)
class ScheduledCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ScheduledCoursesSerializer

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return bm.ScheduledCourse.objects.none()

        lineage = self.request.query_params.get("lineage", "false")
        lineage = True if lineage == "true" else False

        # TODO change into dpt_id
        self.dept_id = self.request.query_params.get("dept_id", None)
        if self.dept_id is not None:
            self.dept_id = int(self.dept_id)
        self.dept = self.request.query_params.get("dept", None)
        if self.dept is not None:
            if self.dept_id is not None:
                raise exceptions.NotAcceptable(
                    detail=f"Please choose beetween dept_id={self.dept_id} and dept={self.dept}"
                )
            try:
                self.dept_id = bm.Department.objects.get(abbrev=self.dept).id
            except bm.Department.DoesNotExist:
                raise exceptions.NotAcceptable(detail="Unknown department")

        self.train_prog = self.request.query_params.get("train_prog", None)
        group_name = self.request.query_params.get("group", None)
        self.tutor = self.request.query_params.get("tutor_name", None)
        work_copy = self.request.query_params.get("work_copy", 0)
        from_date = self.request.query_params.get("from_date", None)
        to_date = self.request.query_params.get("to_date", None)

        if self.tutor is not None:
            try:
                self.tutor = pm.Tutor.objects.get(username=self.tutor)
            except pm.Tutor.DoesNotExist:
                raise exceptions.NotAcceptable(detail="Unknown tutor")

        queryset = (
            bm.ScheduledCourse.objects.all()
            .select_related(
                "course__module__train_prog__department",
                "tutor__display",
                "course__type",
                "course__room_type",
                "course__module__display",
            )
            .prefetch_related(
                "course__groups__train_prog", "room", "course__supp_tutor"
            )
        )
        queryset = queryset.filter(work_copy=work_copy)
        # sanity check
        if group_name is not None and self.train_prog is None:
            raise exceptions.NotAcceptable(
                detail="A training programme should be "
                "given when a group name is given"
            )

        if self.train_prog is not None:
            try:
                if self.dept_id is not None:
                    self.train_prog = bm.TrainingProgramme.objects.get(
                        abbrev=self.train_prog, department=self.dept_id
                    )
                else:
                    self.train_prog = bm.TrainingProgramme.objects.get(
                        abbrev=self.train_prog
                    )
            except bm.TrainingProgramme.DoesNotExist:
                raise exceptions.NotAcceptable(detail="No such training programme")
            except MultipleObjectsReturned:
                raise exceptions.NotAcceptable(
                    detail="Multiple training programme with this name"
                )

        if group_name is not None:
            try:
                declared_group = bm.StructuralGroup.objects.get(
                    name=group_name, train_prog=self.train_prog
                )
                self.groups = {declared_group}
                if lineage:
                    self.groups |= declared_group.ancestor_groups()
            except bm.StructuralGroup.DoesNotExist:
                raise exceptions.NotAcceptable(detail="No such group")
            except:
                raise exceptions.NotAcceptable(detail="Issue with the group")
            queryset = queryset.filter(course__groups__in=self.groups)
        else:
            if self.train_prog is not None:
                queryset = queryset.filter(course__groups__train_prog=self.train_prog)

        if group_name is None and self.train_prog is None:
            if self.dept_id is None:
                if self.tutor is None:
                    pass
                    # raise exceptions.NotAcceptable(
                    #     detail='You should either pick a group and a training programme, or a tutor, or a department')
            else:
                queryset = queryset.filter(
                    course__module__train_prog__department=self.dept_id
                )
            if self.tutor is not None:
                queryset = queryset.filter(
                    Q(tutor=self.tutor) | Q(course__supp_tutor=self.tutor)
                )

        if from_date is not None:
            from_date_time = dt.datetime.fromisoformat(from_date)
        if to_date is not None:
            to_date_time = dt.datetime.fromisoformat(to_date) + dt.timedelta(days=1)
        return queryset.filter(
            start_time__gte=from_date_time, start_time__lte=to_date_time
        )


class RoomFilterSet(filters.FilterSet):
    permission_classes = [IsAdminOrReadOnly]

    dept = filters.CharFilter(field_name="departments__abbrev", required=False)

    class Meta:
        model = bm.Room
        fields = ["dept"]


class RoomsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the rooms.

    Can be filtered as wanted with parameter="dept"[required] of a Room object, with the function RoomsFilterSet
    """

    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomsSerializer
    filterset_class = RoomFilterSet


class ModulesViewSet(viewsets.ModelViewSet):
    """ """

    permission_classes = [IsAdminOrReadOnly]

    queryset = bm.Module.objects.all()
    serializer_class = serializers.ModulesSerializer
    filterset_fields = "__all__"
