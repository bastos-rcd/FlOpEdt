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
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    PolymorphicProxySerializer,
)
from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework import serializers as rfs

from django.utils.decorators import method_decorator
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

from django.apps import apps

import base.models as bm
import people.models as pm

from . import serializers

from api.permissions import IsAdminOrReadOnly

from base.timing import date_to_flopday, days_list, days_index
import datetime as dt


class ScheduledCourseHumanQueryParamsSerializer(rfs.Serializer):
    from_date = rfs.DateField()
    to_date = rfs.DateField()
    tutor = rfs.CharField(required=False)
    dept = rfs.CharField(required=False)
    train_prog = rfs.CharField(required=False)
    struct_group = rfs.CharField(required=False)
    and_transversal = rfs.BooleanField(required=False, default=True)
    lineage = rfs.BooleanField(required=False)

    def validate(self, value):
        if "dept" in value:
            try:
                value["dept_id"] = bm.Department.objects.get(abbrev=value["dept"]).id
                del value["dept"]
            except bm.Department.DoesNotExist:
                raise exceptions.ValidationError(detail={"dept": "Unknown department"})

        if "tutor" in value:
            try:
                value["tutor_id"] = pm.Tutor.objects.get(username=value["tutor"])
                del value["tutor"]
            except pm.Tutor.DoesNotExist:
                raise exceptions.ValidationError(detail={"tutor": "Unknown tutor"})

        if "train_prog" in value:
            if "dept_id" not in value:
                raise exceptions.ValidationError(
                    detail={
                        "train_prog": "If you provide a training programme, you should also provide a department"
                    }
                )
            try:
                value["train_prog_id"] = bm.TrainingProgramme.objects.get(
                    abbrev=value["train_prog"], department=value["dept_id"]
                )
                del value["train_prog"]
                del value["dept_id"]
            except bm.TrainingProgramme.DoesNotExist:
                raise exceptions.ValidationError(
                    detail={"train_prog": "Unknown training programme"}
                )

        if "struct_group" in value:
            if "train_prog_id" not in value:
                raise exceptions.ValidationError(
                    detail={
                        "train_prog": "If you provide a group name, you should also provide a training programme (and a department if training programme name)"
                    }
                )
            try:
                value["struct_group_id"] = bm.StructuralGroup.objects.get(
                    name=value["struct_group"], train_prog=value["train_prog_id"]
                ).id
                del value["train_prog_id"]
            except bm.StructuralGroup.DoesNotExist:
                raise exceptions.NotAcceptable(detail={"struct_group": "Unknown group"})

        value["work_copy"] = 0
        return value


class ScheduledCourseQueryParamsSerializer(rfs.Serializer):
    from_date = rfs.DateField(required=False)
    to_date = rfs.DateField(required=False)
    period_id = rfs.IntegerField(required=False)
    work_copy = rfs.IntegerField(required=False, default=0)
    work_copy_nb = rfs.IntegerField(required=False, default=0)
    tutor_id = rfs.IntegerField(required=False)
    dept_id = rfs.IntegerField(required=False)
    train_prog_id = rfs.IntegerField(required=False)
    struct_group_id = rfs.IntegerField(required=False)
    and_transversal = rfs.BooleanField(required=False, default=True)
    lineage = rfs.BooleanField(required=False)

    def validate(self, value):
        value = super().validate(value)

        # period
        if "period_id" not in value and (
            "from_date" not in value or "to_date" not in value
        ):
            raise exceptions.ValidationError(
                detail={
                    "non_fields_error": f"No parameters on the period. Please choose a from_date and a to_date, or a preiod_id"
                }
            )

        group_keys = [
            k for k in value if k in ["dept_id", "train_prog_id", "struct_group_id"]
        ]
        if len(group_keys) > 1:
            raise exceptions.ValidationError(
                detail={
                    "non_fields_error": "At most 1 group parameter id allowed (department, training programme, group)"
                }
            )

        if "struct_group_id" in value:
            try:
                groups = {bm.StructuralGroup.objects.get(id=value["struct_group_id"])}
                if groups is not None:
                    if value["lineage"]:
                        groups |= groups.ancestor_groups()
                    value["group_ids"] = [gp.id for gp in groups]

                if groups is not None and value["and_transversal"]:
                    tgroups = bm.TransversalGroup.objects.filter(
                        conflicting_groups__in=groups
                    ).distinct("id")
                    value["group_ids"].extend([gp.id for gp in tgroups])
            except bm.StructuralGroup.DoesNotExist:
                pass
            del value["struct_group_id"]

        main_keys = [
            k
            for k in value
            if k in ["tutor_id", "dept_id", "train_prog_id", "group_ids"]
        ]
        if len(main_keys) == 0:
            raise exceptions.ValidationError(
                detail={
                    "non_fields_error": "You should provide a department or a tutor or a training programme or a group"
                }
            )

        return value


class ScheduledCoursesJoinedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get a list of scheduled courses.
    If several parameters apply on groups of people (department, training programme, structural groups),
    only the finest grain filter is used and other group parameters are ignored (filters on structural
    groups if provided, then on training programme if provided, then on department if provided).
    """

    serializer_class = serializers.ScheduledCoursesSerializer

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return bm.ScheduledCourse.objects.none()

        params = self.get_params()

        queryset = bm.ScheduledCourse.objects.filter(
            work_copy=params["work_copy"],
            start_time__gte=dt.datetime.combine(params["from_date"], dt.time(0, 0, 0)),
            start_time__lte=dt.datetime.combine(
                params["to_date"] + dt.timedelta(days=1), dt.time(0, 0, 0)
            ),
        )

        if "tutor_id" in params:
            queryset = queryset.filter(
                Q(tutor=params["tutor_id"]) | Q(course__supp_tutor=params["tutor_id"])
            )

        if "group_ids" in params:
            queryset = queryset.filter(course__groups__in=params["group_ids"])
        elif "train_prog_id" in params:
            queryset = queryset.filter(
                course__module__train_prog=params["train_prog_id"]
            )
        elif "dept_id" in params:
            queryset = queryset.filter(
                course__module__train_prog__department=params["dept_id"]
            )

        pull = self.serializer_class.and_related()
        return queryset.select_related(*pull["select"].keys()).prefetch_related(
            *pull["prefetch"].keys()
        )

    class Meta:
        abstract = True


@extend_schema(parameters=[ScheduledCourseQueryParamsSerializer])
class ScheduledCoursesFullParamViewSet(ScheduledCoursesJoinedViewSet):
    def get_params(self):
        serializer = ScheduledCourseQueryParamsSerializer(
            data=self.request.query_params
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


@extend_schema(parameters=[ScheduledCourseHumanQueryParamsSerializer])
class ScheduledCoursesHumanParamViewSet(ScheduledCoursesJoinedViewSet):
    def get_params(self):
        serializer = ScheduledCourseHumanQueryParamsSerializer(
            data=self.request.query_params
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


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

    permission_classes = [permissions.DjangoModelPermissions]

    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomsSerializer
    filterset_class = RoomFilterSet


class ModuleQueryParamSerializer(rf_s.Serializer):
    dept_id = rf_s.IntegerField(required=False)
    train_prog_id = rf_s.IntegerField(required=False)
    training_period_id = rf_s.IntegerField(required=False)

    def validate(self, value):
        if "dept_id" in value and "train_prog_id" in value:
            try:
                tp = bm.TrainingProgramme.objects.get(id=value["train_prog_id"])
            except bm.TrainingProgramme.DoesNotExist:
                raise exceptions.ValidationError(
                    detail={"train_prog_id": "Unknown training programme."}
                )
            if tp.department.id != value["dept_id"]:
                msg = "Unmatching department and training programme."
                raise exceptions.ValidationError(
                    detail={"train_prog_id": msg, "dept_id": msg}
                )
            del value["dept_id"]
        return value


class ModuleMixinViewSet:
    permission_classes = [permissions.DjangoModelPermissions]

    def get_queryset(self):
        qp_serializer = ModuleQueryParamSerializer(data=self.request.query_params)
        qp_serializer.is_valid(raise_exception=True)
        params = qp_serializer.validated_data

        if "dept_id" in params:
            params["train_prog__department__id"] = params.pop("dept_id")
        if "train_prog_id" in params:
            params["train_prog__id"] = params.pop("train_prog_id")
        if "training_period_id" in params:
            params["training_period__id"] = params.pop("training_period_id")

        return bm.Module.objects.filter(**params)


@extend_schema(parameters=[ModuleQueryParamSerializer])
class ModuleFullViewSet(ModuleMixinViewSet, viewsets.ModelViewSet):
    """
    Read modules without (potentially long) description
    """

    serializer_class = serializers.ModulesFullSerializer


@extend_schema(parameters=[ModuleQueryParamSerializer])
class ModuleViewSet(ModuleMixinViewSet, viewsets.ReadOnlyModelViewSet):
    """
    Modules
    """

    serializer_class = serializers.ModulesSerializer
