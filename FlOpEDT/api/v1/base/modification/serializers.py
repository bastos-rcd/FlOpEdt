from rest_framework import serializers

from api.v1.base.timing.serializers import SchedulingPeriodSerializer

import base.models as bm


class TimetableVersionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = bm.TimetableVersion
        fields = ("id", "minor", "major")


class TimetableVersionFullSerializer(serializers.ModelSerializer):
    period = SchedulingPeriodSerializer()

    class Meta:
        model = bm.TimetableVersion
        fields = ("id", "department_id", "period", "major", "minor")
