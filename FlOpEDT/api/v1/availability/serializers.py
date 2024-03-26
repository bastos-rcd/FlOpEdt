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

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import exceptions, serializers, status

import base.models as bm
from base.rules import can_push_user_availability
from base.timing import Day, flopdate_to_datetime
from people.models import User


# -----------------
# -- PREFERENCES --
# -----------------
class AvailabilitySerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField()
    duration = serializers.DurationField()
    value = serializers.IntegerField()

    class Meta:
        model = bm.UserAvailability
        fields = ("start_time", "duration", "value")


class UserAvailabilitySerializer(AvailabilitySerializer):
    subject_id = serializers.IntegerField(source="user.id")
    subject_type = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_subject_type(self, obj):
        return "user"

    class Meta:
        model = bm.UserAvailability
        fields = ("subject_id", "subject_type", "start_time", "duration", "value")


class RoomAvailabilitySerializer(AvailabilitySerializer):
    subject_id = serializers.IntegerField(source="room.id")
    subject_type = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_subject_type(self, obj):
        return "room"

    class Meta:
        model = bm.RoomAvailability
        fields = ("subject_id", "subject_type", "start_time", "duration", "value")


class AvailabilityFullDayModel:
    def __init__(self, from_date, to_date, subject_id, intervals):
        self.from_date = from_date
        self.to_date = to_date
        self.subject_id = subject_id
        self.intervals = intervals


class UserAvailabilityFullDayModel(AvailabilityFullDayModel):
    subject_type = "user"
    SubjectModel = User
    AvailabilityModel = bm.UserAvailability


class RoomAvailabilityFullDayModel(AvailabilityFullDayModel):
    subject_type = "room"
    SubjectModel = bm.Room
    AvailabilityModel = bm.RoomAvailability


# class AvailabilityFullDaySerializer(serializers.Serializer):
#     date = serializers.DateField()
#     subject_id = serializers.IntegerField()
#     intervals = AvailabilitySerializer(many=True)


class AvailabilityFullDaySerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    subject_id = serializers.IntegerField()
    intervals = AvailabilitySerializer(many=True)

    class Meta:
        abstract = True

    def validate(self, value):
        value = self.create_unsaved_models(value)
        self.check_intervals(value)
        return value

    def check_intervals(self, value):
        super().validate(value)
        epsilon = dt.timedelta(seconds=60)
        from_date = value["from_date"]
        to_date = value["to_date"]
        availability = value["intervals"]
        if len(availability) == 0:
            raise exceptions.ValidationError(
                detail={"intervals": "Empty request"}, code=status.HTTP_400_BAD_REQUEST
            )
        if availability[0].start_time.date() != from_date:
            raise exceptions.ValidationError(
                detail={
                    "intervals": f"Date and intervals do not match: "
                    f"expected {from_date} but got "
                    f"{availability[0].start_time.date()} as "
                    f"date of the starting time of the first interval"
                }
            )

        target_begin_time = dt.datetime.combine(from_date, dt.time(0))
        if abs(availability[0].start_time - target_begin_time) > epsilon:
            raise exceptions.ValidationError(
                detail={
                    "intervals": f"Should start at 00:00, got {availability[0].start_time}"
                }
            )
        availability[0].start_time = target_begin_time

        target_last_duration = (
            dt.datetime.combine(to_date, dt.time(0))
            + (dt.timedelta(hours=24))
            - availability[-1].start_time
        )
        if abs(availability[-1].duration - target_last_duration) > epsilon:
            raise exceptions.ValidationError(
                detail=(
                    {
                        "intervals": f"Should cover the whole period but finishes at "
                        f"{availability[-1].start_time + availability[-1].duration}"
                    }
                )
            )

        for i, (prev, cons) in enumerate(zip(availability[:-1], availability[1:])):
            if abs(prev.start_time + prev.duration - cons.start_time) > epsilon:
                raise exceptions.ValidationError(
                    detail={
                        "intervals": (
                            f"Should be a partition of the period "
                            f"but interval#{i} finishes at {prev.start_time + prev.duration} "
                            f"while interval#{i+1} starts at {cons.start_time}"
                        )
                    }
                )

    def create_unsaved_models(self, value):
        try:
            subject_dict = {
                self.model.subject_type: self.model.SubjectModel.objects.get(
                    id=value["subject_id"]
                )
            }
        except self.model.SubjectModel.DoesNotExist:
            raise exceptions.ValidationError(
                detail={"subject_id": f"Unknown {self.model.subject_type}"}
            )
        value["intervals"] = sorted(
            [
                self.model.AvailabilityModel(
                    start_time=interval["start_time"],
                    duration=interval["duration"],
                    value=interval["value"],
                    **subject_dict,
                )
                for interval in value["intervals"]
            ],
            key=lambda ua: ua.start_time,
        )

        if self.model.subject_type == "user":
            if not can_push_user_availability(
                self.context["request"].user, value["subject_id"]
            ):
                raise exceptions.PermissionDenied(
                    detail={"subject_id": f"Not your availability"}
                )
        elif self.model.subject_type == "room":
            if not self.context["request"].user.has_perm("base.push_roomavailability"):
                raise exceptions.PermissionDenied(
                    detail={"subject_id": f"You cannot push room availability."},
                )
        return value

    def save(self):
        subject_dict = {
            self.model.subject_type: self.model.SubjectModel.objects.get(
                id=self.validated_data["subject_id"]
            )
        }
        self.model.AvailabilityModel.objects.filter(
            date__gte=self.validated_data["from_date"],
            date__lte=self.validated_data["to_date"],
            **subject_dict,
        ).delete()
        for obj in self.validated_data["intervals"]:
            obj.save()
        return self.model(
            self.validated_data["from_date"],
            self.validated_data["to_date"],
            self.validated_data["subject_id"],
            self.validated_data["intervals"],
        )


class AvailabilityDefaultWeekSerializer(AvailabilityFullDaySerializer):
    def validate(self, value):
        """
        Shift dates to default week
        """
        value = super().validate(value)

        if (value["to_date"] - value["from_date"]).days > 6:
            raise exceptions.ValidationError(
                detail={"to_date": "Expected no more than a week!"}
            )

        value["from_date"] = dt.date(1, 1, value["from_date"].isocalendar().weekday)
        value["to_date"] = dt.date(1, 1, value["to_date"].isocalendar().weekday)

        for a in value["intervals"]:
            a.start_time = dt.datetime.combine(
                dt.date(1, 1, a.start_time.isocalendar().weekday),
                a.start_time.time(),
            )

        return value


class UserAvailabilityDefaultWeekSerializer(AvailabilityDefaultWeekSerializer):
    model = UserAvailabilityFullDayModel


class RoomAvailabilityDefaultWeekSerializer(AvailabilityDefaultWeekSerializer):
    model = RoomAvailabilityFullDayModel


class UserAvailabilityFullDaySerializer(AvailabilityFullDaySerializer):
    model = UserAvailabilityFullDayModel


class RoomAvailabilityFullDaySerializer(AvailabilityFullDaySerializer):
    model = RoomAvailabilityFullDayModel
