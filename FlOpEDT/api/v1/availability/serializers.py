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


class UserAvailabilityDayModel:
    subject_type = "user"

    def __init__(self, date, subject_id, intervals):
        self.date = date
        self.subject_id = subject_id
        self.intervals = intervals


class UserAvailabilityDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    subject_id = serializers.IntegerField()
    intervals = AvailabilitySerializer(many=True)

    def check_intervals(self, availability, av_date):
        epsilon = dt.timedelta(seconds=60)
        if len(availability) == 0:
            raise exceptions.APIException(
                detail="Empty request", code=status.HTTP_400_BAD_REQUEST
            )
        if availability[0].start_time.date() != av_date:
            raise exceptions.APIException(
                detail="Date and intervals do not match",
                code=status.HTTP_400_BAD_REQUEST,
            )

        target_begin_time = dt.combine(av_date, dt.time(0))
        if abs(availability[0].start_time - target_begin_time) > epsilon:
            raise exceptions.APIException(
                detail="Should start at 00:00",
                code=status.HTTP_400_BAD_REQUEST,
            )
        availability[0].start_time = target_begin_time

        target_last_duration = (
            target_begin_time + dt.timedelta(hours=24) - availability[-1].start_time
        )
        if abs(availability[-1].duration - target_last_duration) > epsilon:
            raise exceptions.APIException(
                detail="Should cover the whole day",
                code=status.HTTP_400_BAD_REQUEST,
            )

        for prev, cons in zip(availability[:-1], availability[1:]):
            if abs(prev.start_time + prev.duration - cons.start_time) > epsilon:
                raise exceptions.APIException(
                    detail="Should be a partition of the say",
                    code=status.HTTP_400_BAD_REQUEST,
                )

    def create(self, validated_data):
        try:
            user = User.objects.get(id=validated_data["subject_id"])
        except User.DoesNotExist:
            raise exceptions.APIException(
                detail="Unknown user", code=status.HTTP_400_BAD_REQUEST
            )
        availability = sorted(
            [
                bm.UserAvailability(
                    user=user,
                    start_time=interval["start_time"],
                    duration=interval["end_time"] - interval["start_time"],
                    value=interval["value"],
                )
                for interval in validated_data["intervals"]
            ],
            key=lambda ua: ua.start_time,
        )
        self.check_intervals(availability, validated_data)
        for obj in availability:
            obj.save()
        return UserAvailabilityDayModel(
            validated_data["date"],
            validated_data["subject_id"],
            availability,
        )


# class CoursePreferencesSerializer(PreferenceSerializer):
#     class Meta:
#         model = bm.CoursePreference
#         fields = "__all__"


# class RoomPreferencesSerializer(PreferenceSerializer):
#     room = serializers.CharField(source="room.name")

#     class Meta:
#         model = bm.RoomPreference
#         fields = "__all__"
