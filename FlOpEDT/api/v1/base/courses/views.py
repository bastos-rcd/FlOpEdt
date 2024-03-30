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

import django_filters.rest_framework as filters
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, permissions
from rest_framework import serializers as rf_s
from rest_framework import viewsets

import base.models as bm
import people.models as pm
from api.permissions import IsAdminOrReadOnly

from . import serializers


class ScheduledCourseHumanQueryParamsSerializer(  # pylint: disable=abstract-method
    rf_s.Serializer
):
    from_date = rf_s.DateField()
    to_date = rf_s.DateField()
    tutor = rf_s.CharField(required=False)
    dept = rf_s.CharField(required=False)
    train_prog = rf_s.CharField(required=False)
    struct_group = rf_s.CharField(required=False)
    and_transversal = rf_s.BooleanField(required=False, default=True)
    lineage = rf_s.BooleanField(required=False)

    def validate(self, attrs):
        if "dept" in attrs:
            try:
                attrs["dept_id"] = bm.Department.objects.get(abbrev=attrs["dept"]).id
                del attrs["dept"]
            except bm.Department.DoesNotExist as exc:
                raise exceptions.ValidationError(
                    detail={"dept": "Unknown department"}
                ) from exc

        if "tutor" in attrs:
            try:
                attrs["tutor_id"] = pm.Tutor.objects.get(username=attrs["tutor"])
                del attrs["tutor"]
            except pm.Tutor.DoesNotExist as exc:
                raise exceptions.ValidationError(
                    detail={"tutor": "Unknown tutor"}
                ) from exc

        if "train_prog" in attrs:
            if "dept_id" not in attrs:
                raise exceptions.ValidationError(
                    detail={
                        "train_prog": "If you provide a training programme, "
                        "you should also provide a department"
                    }
                )
            try:
                attrs["train_prog_id"] = bm.TrainingProgramme.objects.get(
                    abbrev=attrs["train_prog"], department=attrs["dept_id"]
                )
                del attrs["train_prog"]
                del attrs["dept_id"]
            except bm.TrainingProgramme.DoesNotExist as exc:
                raise exceptions.ValidationError(
                    detail={"train_prog": "Unknown training programme"}
                ) from exc

        if "struct_group" in attrs:
            if "train_prog_id" not in attrs:
                raise exceptions.ValidationError(
                    detail={
                        "train_prog": "If you provide a group name, you should also provide "
                        "a training programme (and a department if training programme name)"
                    }
                )
            try:
                attrs["struct_group_id"] = bm.StructuralGroup.objects.get(
                    name=attrs["struct_group"], train_prog=attrs["train_prog_id"]
                ).id
                del attrs["train_prog_id"]
            except bm.StructuralGroup.DoesNotExist as exc:
                raise exceptions.NotAcceptable(
                    detail={"struct_group": "Unknown group"}
                ) from exc

        attrs["version__major"] = 0
        return attrs


class ScheduledCourseQueryParamsSerializer(  # pylint: disable=abstract-method
    rf_s.Serializer
):
    from_date = rf_s.DateField(required=False)
    to_date = rf_s.DateField(required=False)
    period_id = rf_s.IntegerField(required=False)
    version = rf_s.CharField(required=False, default="elected")
    major_version = rf_s.IntegerField(required=False, default=0)
    tutor_id = rf_s.IntegerField(required=False)
    dept_id = rf_s.IntegerField(required=False)
    train_prog_id = rf_s.IntegerField(required=False)
    struct_group_id = rf_s.IntegerField(required=False)
    and_transversal = rf_s.BooleanField(required=False, default=True)
    lineage = rf_s.BooleanField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # period
        if "period_id" not in attrs and (
            "from_date" not in attrs or "to_date" not in attrs
        ):
            raise exceptions.ValidationError(
                detail={
                    "non_fields_error": "No parameters on the period. "
                    "Please choose a from_date and a to_date, or a period_id"
                }
            )

        group_keys = [
            k for k in attrs if k in ["dept_id", "train_prog_id", "struct_group_id"]
        ]
        if len(group_keys) > 1:
            raise exceptions.ValidationError(
                detail={
                    "non_fields_error": "At most 1 group parameter id allowed "
                    "(department, training programme, group)"
                }
            )

        if "struct_group_id" in attrs:
            try:
                group = bm.StructuralGroup.objects.get(id=attrs["struct_group_id"])
                if attrs["lineage"]:
                    groups = group.and_ancestors()
                else:
                    groups = {group}
                attrs["group_ids"] = [gp.id for gp in groups]

                if attrs["and_transversal"]:
                    tgroups = bm.TransversalGroup.objects.filter(
                        conflicting_groups__in=groups
                    ).distinct("id")
                    attrs["group_ids"].extend([gp.id for gp in tgroups])
            except bm.StructuralGroup.DoesNotExist:
                pass
            del attrs["struct_group_id"]

        main_keys = [
            k
            for k in attrs
            if k in ["tutor_id", "dept_id", "train_prog_id", "group_ids"]
        ]
        if len(main_keys) == 0:
            raise exceptions.ValidationError(
                detail={
                    "non_fields_error": "You should provide a department "
                    "or a tutor or a training programme or a group"
                }
            )

        return attrs


class ScheduledCoursesJoinedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get a list of scheduled courses.
    If several parameters apply on groups of people
    (department, training programme, structural groups),
    only the finest grain filter is used and other group parameters are ignored
    (filters on structural groups if provided, then on training programme if provided,
    then on department if provided).
    """

    serializer_class = serializers.ScheduledCoursesSerializer

    def get_params(self):
        raise NotImplementedError

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return bm.ScheduledCourse.objects.none()

        params = self.get_params()

        queryset = bm.ScheduledCourse.objects.filter(
            version__major=params["major_version"],
            start_time__gte=dt.datetime.combine(params["from_date"], dt.time(0, 0, 0)),
            start_time__lte=dt.datetime.combine(
                params["to_date"] + dt.timedelta(days=1), dt.time(0, 0, 0)
            ),
        )

        if "tutor_id" in params:
            queryset = queryset.filter(
                Q(tutor=params["tutor_id"]) | Q(course__supp_tutors=params["tutor_id"])
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


# FIXME Define create and update methods for serializers
# pylint: disable=abstract-method


class ModuleQueryParamSerializer(rf_s.Serializer):
    dept_id = rf_s.IntegerField(required=False)
    train_prog_id = rf_s.IntegerField(required=False)
    training_period_id = rf_s.IntegerField(required=False)

    def validate(self, attrs):
        if "dept_id" in attrs and "train_prog_id" in attrs:
            try:
                tp = bm.TrainingProgramme.objects.get(id=attrs["train_prog_id"])
            except bm.TrainingProgramme.DoesNotExist as exc:
                raise exceptions.ValidationError(
                    detail={"train_prog_id": "Unknown training programme."}
                ) from exc
            if tp.department.id != attrs["dept_id"]:
                msg = "Unmatching department and training programme."
                raise exceptions.ValidationError(
                    detail={"train_prog_id": msg, "dept_id": msg}
                )
            del attrs["dept_id"]
        return attrs


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


class RoomFilterSet(filters.FilterSet):
    permission_classes = [IsAdminOrReadOnly]

    dept = filters.CharFilter(field_name="departments__abbrev", required=False)

    class Meta:
        model = bm.Room
        fields = ["dept"]


class RoomsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the rooms.

    Can be filtered as wanted with parameter="dept"[required] of a Room object,
    with the function RoomsFilterSet
    """

    permission_classes = [permissions.DjangoModelPermissions]

    queryset = bm.Room.objects.all()
    serializer_class = serializers.RoomsSerializer
    filterset_class = RoomFilterSet


class TimetableVersionQPS(rf_s.Serializer):
    ids = rf_s.ListField(child=rf_s.IntegerField())


@extend_schema(parameters=[TimetableVersionQPS])
class TimetableVersionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.TimetableVersionSerializer

    def get_queryset(self):
        qp_serializer = TimetableVersionQPS(data=self.request.query_params)
        qp_serializer.is_valid(raise_exception=True)
        params = qp_serializer.validated_data

        return bm.TimetableVersion.objects.filter(id__in=params["ids"])
