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

from rest_framework import serializers, exceptions, status
import base.models as bm
from people.models import User
from base.timing import Day, flopdate_to_datetime
import datetime as dt


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
    subject_type = serializers.ReadOnlyField(default="user")

    class Meta:
        model = bm.UserAvailability
        fields = ("subject_id", "subject_type", "start_time", "duration", "value")


class AvailabilityFullDayModel:
    def __init__(self, date, subject_id, intervals):
        self.date = date
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
    date = serializers.DateField()
    subject_id = serializers.IntegerField()
    intervals = AvailabilitySerializer(many=True)

    class Meta:
        abstract = True

    def check_intervals(self, availability, av_date):
        epsilon = dt.timedelta(seconds=60)
        if len(availability) == 0:
            raise exceptions.APIException(
                detail="Empty request", code=status.HTTP_400_BAD_REQUEST
            )
        if availability[0].start_time.date() != av_date:
            raise exceptions.APIException(
                detail=(
                    f"Date and intervals do not match: "
                    f"expected {av_date} but got "
                    f"{availability[0].start_time.date()} as "
                    f"date of the starting time of the first interval"
                ),
                code=status.HTTP_400_BAD_REQUEST,
            )

        target_begin_time = dt.datetime.combine(av_date, dt.time(0))
        if abs(availability[0].start_time - target_begin_time) > epsilon:
            raise exceptions.APIException(
                detail=f"Should start at 00:00, got {availability[0].start_time}",
                code=status.HTTP_400_BAD_REQUEST,
            )
        availability[0].start_time = target_begin_time

        target_last_duration = (
            target_begin_time + dt.timedelta(hours=24) - availability[-1].start_time
        )
        if abs(availability[-1].duration - target_last_duration) > epsilon:
            raise exceptions.APIException(
                detail=(
                    f"Should cover the whole day but finishes at "
                    f"{availability[-1].start_time + availability[-1].duration}"
                ),
                code=status.HTTP_400_BAD_REQUEST,
            )

        for i, (prev, cons) in enumerate(zip(availability[:-1], availability[1:])):
            if abs(prev.start_time + prev.duration - cons.start_time) > epsilon:
                raise exceptions.APIException(
                    detail=(
                        f"Should be a partition of the day "
                        f"but interval#{i} finishes at {prev.start_time + prev.duration} "
                        f"while interval#{i+1} starts at {cons.start_time}"
                    ),
                    code=status.HTTP_400_BAD_REQUEST,
                )

    def create(self, validated_data):

        try:
            subject_dict = {
                self.model.subject_type: self.model.SubjectModel.objects.get(
                    id=validated_data["subject_id"]
                )
            }
        except self.model.SubjectModel.DoesNotExist:
            raise exceptions.APIException(
                detail="Unknown user", code=status.HTTP_400_BAD_REQUEST
            )
        availability = sorted(
            [
                self.model.AvailabilityModel(
                    start_time=interval["start_time"],
                    duration=interval["duration"],
                    value=interval["value"],
                    **subject_dict,
                )
                for interval in validated_data["intervals"]
            ],
            key=lambda ua: ua.start_time,
        )
        self.check_intervals(availability, validated_data["date"])
        for obj in availability:
            obj.save()
        return self.model(
            validated_data["date"],
            validated_data["subject_id"],
            availability,
        )


class UserAvailabilityFullDaySerializer(AvailabilityFullDaySerializer):
    model = UserAvailabilityFullDayModel


class RoomAvailabilityFullDaySerializer(AvailabilityFullDaySerializer):
    model = RoomAvailabilityFullDayModel
